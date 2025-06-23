def generate_chord_svg(chord_name):
    # В реальном приложении здесь будет запрос к базе данных
    # Для примера - захардкоженные данные
    chord_data = {
        'C': {
            'positions': [{'string': 5, 'fret': 3}, {'string': 4, 'fret': 2}, {'string': 2, 'fret': 1}],
            'open_strings': [0, 1, 3],
            'muted_strings': [6]
        },
        'G': {
            'positions': [{'string': 6, 'fret': 3}, {'string': 5, 'fret': 2}, {'string': 1, 'fret': 3}],
            'open_strings': [2, 3, 4],
            'muted_strings': []
        },
        'D': {
            'positions': [{'string': 4, 'fret': 0}, {'string': 3, 'fret': 2}, {'string': 2, 'fret': 3}, {'string': 1, 'fret': 2}],
            'open_strings': [5, 6],
            'muted_strings': []
        },
        'Am': {
            'positions': [{'string': 4, 'fret': 2}, {'string': 3, 'fret': 2}, {'string': 2, 'fret': 1}],
            'open_strings': [0, 1, 5],
            'muted_strings': [6]
        },
        'Em': {
            'positions': [{'string': 5, 'fret': 2}, {'string': 4, 'fret': 2}],
            'open_strings': [0, 1, 2, 3, 6],
            'muted_strings': []
        }
    }
    
    chord = chord_data.get(chord_name, chord_data['C'])
    
    width = 200
    height = 250
    string_count = 6
    fret_count = 4
    
    # Начало SVG
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    
    # Рамка
    svg += f'<rect x="10" y="10" width="{width-20}" height="{height-20}" fill="none" stroke="black" stroke-width="2" rx="5"/>'
    
    # Гриф гитары
    svg += f'<rect x="50" y="30" width="10" height="{height-60}" fill="#8B4513"/>'
    
    # Струны
    string_spacing = (height - 60) / (string_count - 1)
    for i in range(string_count):
        y = 30 + i * string_spacing
        svg += f'<line x1="50" y1="{y}" x2="{width-50}" y2="{y}" stroke="gray" stroke-width="{1 if i in [0,5] else 0.5}"/>'
    
    # Лады
    fret_spacing = (width - 100) / (fret_count - 1)
    for i in range(fret_count):
        x = 50 + i * fret_spacing
        svg += f'<line x1="{x}" y1="30" x2="{x}" y2="{height-30}" stroke="black" stroke-width="{1.5 if i == 0 else 1}"/>'
    
    # Ноты (кружки)
    for pos in chord['positions']:
        string_idx = pos['string'] - 1
        fret_idx = pos['fret']
        
        if fret_idx == 0:  # Открытая струна
            x = 25
            y = 30 + string_idx * string_spacing
            svg += f'<circle cx="{x}" cy="{y}" r="8" fill="white" stroke="black"/>'
        else:  # Зажатая струна
            x = 50 + (fret_idx - 0.5) * fret_spacing
            y = 30 + string_idx * string_spacing
            svg += f'<circle cx="{x}" cy="{y}" r="10" fill="black"/>'
    
    # Открытые струны
    for string_idx in chord['open_strings']:
        y = 30 + (string_idx - 1) * string_spacing
        svg += f'<text x="25" y="{y+5}" text-anchor="middle" font-size="14">O</text>'
    
    # Заглушенные струны
    for string_idx in chord['muted_strings']:
        y = 30 + (string_idx - 1) * string_spacing
        svg += f'<text x="25" y="{y+5}" text-anchor="middle" font-size="14">X</text>'
    
    # Название аккорда
    svg += f'<text x="{width//2}" y="20" text-anchor="middle" font-size="16" font-weight="bold">{chord_name}</text>'
    
    svg += '</svg>'
    return svg