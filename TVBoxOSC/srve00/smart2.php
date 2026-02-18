<?php
error_reporting(E_ALL);
ini_set('display_errors', 1); // 调试时显示错误
header('Content-Type: text/plain; charset=utf-8');
date_default_timezone_set("Asia/Shanghai");
// session_start(); //不使用session

// 核心配置
const CONFIG = [
    'upstream'   => [
    'http://livesmart5.robyang.dpdns.org:11799/', 
    'http://livesmart1.robyang.dpdns.org:11799/', 
    'http://livesmart2.robyang.dpdns.org:11799/', 
    'http://livesmart3.robyang.dpdns.org:11799/', 
    'http://livesmart4.robyang.dpdns.org:11799/'], 
    'list_url'   => 'https://cdn.jsdelivr.net/gh/hostemail/cdn@main/data/smart.txt',
    'backup_url' => 'https://cdn.jsdelivr.net/gh/hostemail/cdn@main/data/smart1.txt', 
    'token_ttl'  => 2400,  // 40分钟有效期
    'cache_ttl'  => 3600,  // 频道列表缓存1小时
    'fallback'   => 'https://www.youtube.com/watch?v=MV9mI0GChwo', 
    'clear_key'  => 'leifeng'
];


// const CONFIG = [
//     'upstream'   => [
//     'http://198.16.100.186:11799/', 
//     'http://50.7.92.106:11799/', 
//     'http://50.7.234.10:11799/',
//     'http://50.7.220.170:11799/', 
//     'http://67.159.6.34:11799/'], 
//     'list_url'   => 'https://cdn.jsdelivr.net/gh/hostemail/cdn@main/data/smart.txt',
//     'backup_url' => 'https://cdn.jsdelivr.net/gh/hostemail/cdn@main/data/smart1.txt', 
//     'token_ttl'  => 2400,  // 40分钟有效期
//     'cache_ttl'  => 3600,  // 频道列表缓存1小时
//     'fallback'   => 'https://www.youtube.com/watch?v=MV9mI0GChwo', 
//     'clear_key'  => 'leifeng'
// ];

// 获取当前轮询的上游服务器
function getUpstream() {
    static $index = 0;
    $upstreams = CONFIG['upstream'];
    $current = $upstreams[$index % count($upstreams)];
    $index++;
    return $current;
}

// 主路由控制
try {
    if (isset($_GET['action']) && $_GET['action'] === 'clear_cache') {
        clearCache();
    } elseif (!isset($_GET['id'])) {
        sendTXTList();
    } else {
        handleChannelRequest();
    }
} catch (Exception $e) {
    header('HTTP/1.1 503 Service Unavailable');
    exit("系统维护中，请稍后重试\n错误详情：" . $e->getMessage());
}

function fetch_remote_file($url, $timeout = 5)
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_CONNECTTIMEOUT => $timeout,
        CURLOPT_TIMEOUT => $timeout,
        CURLOPT_SSL_VERIFYPEER => true, // 如果有自签证书，可以设为 false
        CURLOPT_HTTPHEADER => ['Cache-Control: no-cache']
    ]);

    $response = curl_exec($ch);

    if (curl_errno($ch)) {
        $err = curl_error($ch);
        curl_close($ch);
        throw new RuntimeException("CURL 请求失败: $err");
    }

    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($http_code >= 400) {
        throw new RuntimeException("远程服务器返回 HTTP $http_code 错误");
    }

    return $response;
}

// 缓存清除
function clearCache() {
    error_log("[ClearCache] ClientIP:{$_SERVER['REMOTE_ADDR']}, Key:".($_GET['key']??'null'));

    $validKey = $_GET['key'] ?? '';
    $isLocal = in_array($_SERVER['REMOTE_ADDR'], ['127.0.0.1', '::1']);
    if (!$isLocal && !hash_equals(CONFIG['clear_key'], $validKey)) {
        header('HTTP/1.1 403 Forbidden');
        exit("权限验证失败\nIP: {$_SERVER['REMOTE_ADDR']}\n密钥状态: ".(empty($validKey)?'未提供':'无效'));
    }

    $results = [];
    $cacheType = '';

    if (extension_loaded('apcu')) {
        $cacheType = 'APCu';
        $results[] = apcu_clear_cache() ? '✅ APCu缓存已清除' : '❌ APCu清除失败';
    } else {
        $results[] = '⚠️ APCu扩展未安装';
    }

    try {
        $list = getChannelList(true);
        if (empty($list)) throw new Exception("频道列表为空");
        $results[] = '📡 频道列表已重建 数量:' . count($list);
        $cacheType = $cacheType ?: '无缓存扩展';
        $results[] = "🔧 使用缓存类型: $cacheType";
    } catch (Exception $e) {
        $results[] = '⚠️ 列表重建失败: ' . $e->getMessage();
    }
    /* 不使用session
    $_SESSION = [];
    if (session_destroy()) {
        $results[] = '✅ Session已销毁';
    }
    */
    header('Cache-Control: no-store');
    exit(implode("\n", $results));
}

// 生成TXT主列表
function sendTXTList() {
    header("Cache-Control: no-store, no-cache, must-revalidate");
    header("Pragma: no-cache");
    header("Expires: 0");

    try {
        $channels = getChannelList();
    } catch (Exception $e) {
        header('HTTP/1.1 500 Internal Server Error');
        exit("无法获取频道列表: " . $e->getMessage());
    }

    $baseUrl  = getBaseUrl();
    $script   = basename(__FILE__);
    
    $grouped = [];
    foreach ($channels as $chan) {
        $grouped[$chan['group']][] = $chan;
    }

    $output = '';
    foreach ($grouped as $group => $items) {
        $output .= htmlspecialchars($group) . ",#genre#\n";
        foreach ($items as $chan) {
            $output .= sprintf("%s,%s/%s?id=%s\n",
                htmlspecialchars($chan['name']),
                $baseUrl,
                $script,
                urlencode($chan['id'])
            );
        }
        $output .= "\n";
    }

    header('Content-Disposition: inline; filename="channels_'.time().'.txt"');
    echo trim($output);
}

// 获取频道列表（仅内存缓存）
function getChannelList($forceRefresh = false) {
    if (!$forceRefresh && extension_loaded('apcu')) {
        $cached = apcu_fetch('smart_channels');
        if ($cached !== false) {
            return $cached;
        }
    }

    $raw = fetchWithRetry(CONFIG['list_url'], 3);
    if ($raw === false) {
        $raw = fetchWithRetry(CONFIG['backup_url'], 2);
        if ($raw === false) {
            throw new Exception("所有数据源均不可用");
        }
    }

    $list = [];
    $currentGroup = '默认分组';
    foreach (explode("\n", trim($raw)) as $line) {
        $line = trim($line);
        if (!$line) continue;

        if (strpos($line ?? '', '#genre#') !== false) {
            $currentGroup = trim(str_replace(',#genre#', '', $line));
            continue;
        }

        $id = null;
        if (preg_match('/\/\/:id=(\w+)/', $line, $m)) {
            $id = $m[1];
            $name = trim(explode(',', $line)[0]); // 修复括号
        } elseif (preg_match('/[?&]id=([^&]+)/', $line, $m)) {
            $id = $m[1];
            $name = trim(explode(',', $line)[0]); // 修复括号
        }

        if ($id) {
            $list[] = [
                'id'    => $id,
                'name'  => $name,
                'group' => $currentGroup,
                'logo'  => ''
            ];
        }
    }

    if (empty($list)) {
        throw new Exception("频道列表解析失败");
    }

    if (extension_loaded('apcu')) {
        apcu_store('smart_channels', $list, CONFIG['cache_ttl']);
    }

    return $list;
}

// 带重试机制的获取函数
function fetchWithRetry($url, $maxRetries = 3) {
    $retryDelay = 500; // 毫秒
    $lastError = '';
    
    for ($i = 0; $i < $maxRetries; $i++) {
        try {
            $ctx = stream_context_create([
                'http' => [
                    'timeout' => 5,
                    'header' => "User-Agent: Mozilla/5.0\r\n"
                ],
                'ssl' => [
                    'verify_peer' => false,
                    'verify_peer_name' => false
                ]
            ]);
            
            $raw = @fetch_remote_file($url, false, $ctx);
            if ($raw !== false) {
                return $raw;
            }
            $lastError = error_get_last()['message'] ?? '未知错误';
            
        } catch (Exception $e) {
            $lastError = $e->getMessage();
        }
        
        if ($i < $maxRetries - 1) {
            usleep($retryDelay * 1000);
            $retryDelay *= 2; // 指数退避
        }
    }
    
    error_log("[Fetch] 获取失败: $url, 错误: $lastError");
    return false;
}

// 处理频道请求
function handleChannelRequest() {
    $channelId = $_GET['id'];
    $tsFile    = $_GET['ts'] ?? '';
    $token     = manageToken();

    if ($tsFile) {
        proxyTS($channelId, $tsFile);
    } else {
        generateM3U8($channelId, $token);
    }
}

/* Token管理V1:基于session 
function manageToken() {
    $token = $_GET['token'] ?? '';
    
    if (empty($_SESSION['token']) || 
        !hash_equals($_SESSION['token'], $token) || 
        (time() - $_SESSION['token_time']) > CONFIG['token_ttl']) {
        
        $token = bin2hex(random_bytes(16));
        $_SESSION = [
            'token'      => $token,
            'token_time' => time()
        ];
        
        if (isset($_GET['ts'])) {
            $url = getBaseUrl() . '/' . basename(__FILE__) . '?' . http_build_query([
                'id'    => $_GET['id'],
                'ts'    => $_GET['ts'],
                'token' => $token
            ]);
            header("Location: $url");
            exit();
        }
    }
    
    return $token;
}
*/

// Token管理V2:无session 
function manageToken() {
    $token = $_GET['token'] ?? '';
    
    // 验证现有Token是否有效（含40分钟时效检查）
    if (!empty($token) && validateToken($token)) {
        return $token;
    }
    
    // 生成新Token（32位）
    $newToken = bin2hex(random_bytes(16)) . ':' . time(); // 格式：随机值:时间戳
    
    // TS请求重定向逻辑保持不变
    if (isset($_GET['ts'])) {
        $url = getBaseUrl() . '/' . basename(__FILE__) . '?' . http_build_query([
            'id'    => $_GET['id'],
            'ts'    => $_GET['ts'],
            'token' => $newToken
        ]);
        header("Location: $url");
        exit();
    }
    
    return $newToken;
}

function validateToken($token) {
    // 解析Token格式：随机值:时间戳
    $parts = explode(':', $token);
    if (count($parts) !== 2) return false;
    
    $timestamp = (int)$parts[1];
    $currentTime = time();
    
    // 验证时效性（40分钟内有效）
    return ($currentTime - $timestamp) <= CONFIG['token_ttl']; // 2400秒=40分钟
}


// 生成M3U8播放列表
function generateM3U8($channelId, $token) {
    $upstream = getUpstream();
    $authUrl = $upstream. "$channelId/playlist.m3u8?" . http_build_query([
        'tid'  => 'mc42afe745533',
        'ct'   => intval(time() / 150),
        'tsum' => md5("tvata nginx auth module/$channelId/playlist.m3u8mc42afe745533" . intval(time() / 150))
    ]);
    
    $content = fetchUrl($authUrl);
    if (strpos($content, '404 Not Found') !== false) {
        header("Location: " . CONFIG['fallback']);
        exit();
    }
    
    $baseUrl = getBaseUrl() . '/' . basename(__FILE__);
    $content = preg_replace_callback('/(\S+\.ts)/', function($m) use ($baseUrl, $channelId, $token) {
    return "$baseUrl?id=" . urlencode($channelId) . "&ts=" . urlencode($m[1]) . "&token=" . urlencode($token);
    }, $content ?? '');
    
    header('Content-Type: application/vnd.apple.mpegurl');
    header('Content-Disposition: inline; filename="' . $channelId . '.m3u8"');
    echo $content;
}

// 代理TS流
function proxyTS($channelId, $tsFile) {
    $upstream = getUpstream();
    $url = $upstream . "$channelId/$tsFile";
    $data = fetchUrl($url);
    
    if ($data === null) {
        header('HTTP/1.1 404 Not Found');
        exit();
    }
    
    header('Content-Type: video/MP2T');
    header('Content-Length: ' . strlen($data));
    echo $data;
}

// 通用URL获取
function fetchUrl($url) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => ["CLIENT-IP: 127.0.0.1", "X-FORWARDED-FOR: 127.0.0.1"],
        CURLOPT_TIMEOUT        => 5,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_FOLLOWLOCATION => true
    ]);
    
    $data = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    return $code == 200 ? $data : null;
}

// 获取基础URL
function getBaseUrl() {
    return (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http') 
           . "://$_SERVER[HTTP_HOST]";
}