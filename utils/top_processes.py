import psutil

# ========== 获取所有进程 ==========
def get_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'memory_info', 'cpu_percent']):
        try:
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'user': proc.info['username'] or 'root',
                'memory_mb': proc.info['memory_info'].rss / 1024**2,
                'memory_percent': proc.info['memory_percent'],
                'cpu_percent': proc.info['cpu_percent']
            })
        except:
            pass

    processes.sort(key=lambda x: x['memory_mb'], reverse=True)
    return processes