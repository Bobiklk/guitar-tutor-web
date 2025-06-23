def generate_strumming_pattern(pattern):
    symbols = {
        '↓': 'M 10,20 L 40,50',  # Вниз
        '↑': 'M 10,50 L 40,20',  # Вверх
        'x': 'M 10,20 L 40,50 M 10,50 L 40,20',  # Приглушение
        ' ': 'M 25,35 L 25,35'  # Пауза
    }
    
    width = 300
    height = 100
    items = pattern.split()
    item_count = len(items)
    item_width = width / item_count if item_count > 0 else 0
    
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    
    # Фон
    svg += f'<rect width="100%" height="100%" fill="#f5f5f5" rx="5"/>'
    
    # Название паттерна
    svg += f'<text x="10" y="20" font-size="14">{pattern}</text>'
    
    # Сетка
    for i in range(item_count + 1):
        x = i * item_width
        svg += f'<line x1="{x}" y1="30" x2="{x}" y2="{height-10}" stroke="#ddd"/>'
    
    # Символы
    for i, symbol in enumerate(items):
        x_center = (i + 0.5) * item_width
        y_center = 60
        
        if symbol in symbols:
            path = symbols[symbol]
            svg += f'<path d="{path}" transform="translate({x_center-25},{y_center-35})" stroke="black" stroke-width="2" fill="none"/>'
        
        # Номер доли
        svg += f'<text x="{x_center}" y="{height-5}" text-anchor="middle" font-size="12">{i+1}</text>'
    
    svg += '</svg>'
    return svg