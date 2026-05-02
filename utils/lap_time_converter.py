def format_time(ms):
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000

    return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
