<?php
/**
 * m3u8/ts 代理（优化版：TS 流式转发 + failover + Range 透传 + 修复 strpos 判断）
 */

error_reporting(0); // 生产建议关闭 E_ALL（E_ALL 会增加开销）
date_default_timezone_set("Asia/Shanghai");

// CORS / OPTIONS
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');
header('Access-Control-Allow-Headers: X-Requested-With, Content-Type, Range');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

// 参数
$name = $_GET['id'] ?? '';
$ts   = $_GET['ts'] ?? '';

if ($name === '') {
    http_response_code(400);
    echo "Missing id";
    exit;
}

// 简单安全过滤（避免奇怪路径注入）
$name = preg_replace('~[^a-zA-Z0-9_\-]~', '', $name);
$ts   = $ts ? preg_replace('~[^a-zA-Z0-9_\-\.\/]~', '', $ts) : '';

// 多服务器
$serverIPs = [
    '38.135.24.88',
];

function selectServer($servers, $name = '') {
    if (!empty($name)) {
        $index = crc32($name) % count($servers);
        return $servers[$index];
    }
    return $servers[array_rand($servers)];
}

// 把服务器列表“旋转”一下：从选中的开始依次尝试
function rotatedServers($servers, $first) {
    $idx = array_search($first, $servers, true);
    if ($idx === false) return $servers;
    return array_merge(array_slice($servers, $idx), array_slice($servers, 0, $idx));
}

// ======== CURL：流式转发 TS（不进内存）========
function curl_stream_to_client($url, array $headers, $timeout = 10) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_HEADER            => false,
        CURLOPT_FOLLOWLOCATION    => true,
        CURLOPT_CONNECTTIMEOUT    => 2,
        CURLOPT_TIMEOUT           => $timeout,
        CURLOPT_SSL_VERIFYPEER    => false,
        CURLOPT_SSL_VERIFYHOST    => false,
        CURLOPT_HTTPHEADER        => $headers,
        CURLOPT_RETURNTRANSFER    => false,  // 关键：不返回字符串
        CURLOPT_BINARYTRANSFER    => true,
        CURLOPT_BUFFERSIZE        => 262144, // 256KB buffer
        CURLOPT_WRITEFUNCTION     => function($ch, $data) {
            echo $data;
            // 尽量及时 flush，降低 FPM 内存堆积
            if (function_exists('fastcgi_finish_request')) {
                // 不在这里 finish_request，会中断；只 flush
            }
            @ob_flush();
            flush();
            return strlen($data);
        },
    ]);

    $ok = curl_exec($ch);
    $errno = curl_errno($ch);
    $code  = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($ok === false || $errno !== 0) return [false, 0];
    return [$code >= 200 && $code < 300, $code];
}

// ======== CURL：获取文本（m3u8 体积小，允许进内存）========
function curl_get_text($url, array $headers, $timeout = 8) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_HEADER            => false,
        CURLOPT_FOLLOWLOCATION    => true,
        CURLOPT_CONNECTTIMEOUT    => 2,
        CURLOPT_TIMEOUT           => $timeout,
        CURLOPT_SSL_VERIFYPEER    => false,
        CURLOPT_SSL_VERIFYHOST    => false,
        CURLOPT_HTTPHEADER        => $headers,
        CURLOPT_RETURNTRANSFER    => true,
    ]);

    $data  = curl_exec($ch);
    $errno = curl_errno($ch);
    $code  = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($errno !== 0 || $data === false || $code === 404) {
        return [null, $code ?: 0];
    }
    return [$data, $code];
}

// 构建透传请求头（Range 很重要）
$upHeaders = [];
if (!empty($_SERVER['HTTP_RANGE'])) {
    $upHeaders[] = 'Range: ' . $_SERVER['HTTP_RANGE'];
}

// 你原本伪造的 IP 头，实际大多没用，还可能导致上游走不同逻辑；建议去掉
// $upHeaders[] = "CLIENT-IP: 127.0.0.1";
// $upHeaders[] = "X-FORWARDED-FOR: 127.0.0.1";

$selectedIP = selectServer($serverIPs, $name);
$serversTry = rotatedServers($serverIPs, $selectedIP);

$basePort = 11799;

// ==============================
// TS 代理（流式）
// ==============================
if ($ts) {
    header('Content-Type: video/mp2t');
    header('Cache-Control: public, max-age=30');
    header('Expires: ' . gmdate('D, d M Y H:i:s', time() + 30) . ' GMT');
    header('Accept-Ranges: bytes');

    // 依次尝试服务器
    foreach ($serversTry as $ip) {
        $url = "http://{$ip}:{$basePort}/{$name}/{$ts}";
        [$ok, $code] = curl_stream_to_client($url, $upHeaders, 10);
        if ($ok) {
            exit;
        }
        // 失败继续下一个
    }

    http_response_code(404);
    echo "Error: TS not found.";
    exit;
}

// ==============================
// M3U8 代理（文本）
// ==============================
header('Content-Type: application/vnd.apple.mpegurl');

// 给 m3u8 也加短缓存，减少频繁拉取（按需调整）
header('Cache-Control: public, max-age=2');
header('Expires: ' . gmdate('D, d M Y H:i:s', time() + 2) . ' GMT');

$seed = "tvata nginx auth module";
$tid  = "mc42afe834703";

$playlistPath = "/{$name}/playlist.m3u8";

// ct/tsum
$t    = (string)intval(time() / 150);
$str  = $seed . $playlistPath . $tid . $t;
$tsum = md5($str);
$link = http_build_query(["ct" => $t, "tsum" => $tsum]);

$self = $_SERVER['PHP_SELF'];

// failover 获取 m3u8
$result = null;
foreach ($serversTry as $ip) {
    $url = "http://{$ip}:{$basePort}{$playlistPath}?tid={$tid}&{$link}";
    [$data, $code] = curl_get_text($url, $upHeaders, 8);
    if (!empty($data) && $code >= 200 && $code < 300 && strpos($data, "EXTM3U") !== false) {
        $result = $data;
        break;
    }
}

if ($result === null) {
    header("Location: https://iptv.gv.uy/notv.mp4");
    exit;
}

// 重写 ts 行（只改真正的媒体行，避免误伤）
$lines = preg_split("/\r\n|\n|\r/", $result);
$out = [];

foreach ($lines as $line) {
    $line = trim($line);
    if ($line === '') continue;

    if ($line[0] === '#') {
        $out[] = $line;
        continue;
    }

    // 媒体 URL：相对/绝对都兼容
    if (stripos($line, '.ts') !== false) {
        // 如果上游给的是完整 URL，取路径最后一段也能用；更严谨可 parse_url
        $tsName = $line;

        // 绝对 URL 时，取 path + query（按你的需求也可只取 basename）
        if (stripos($tsName, 'http://') === 0 || stripos($tsName, 'https://') === 0) {
            $p = parse_url($tsName);
            $tsName = ltrim(($p['path'] ?? ''), '/');
            if (!empty($p['query'])) $tsName .= '?' . $p['query'];
        }

        $out[] = $self . "?id=" . rawurlencode($name) . "&ts=" . rawurlencode($tsName);
    } else {
        $out[] = $line;
    }
}

echo implode("\n", $out) . "\n";
exit;