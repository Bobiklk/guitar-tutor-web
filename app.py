from flask import Flask, render_template, request, jsonify, session
import sqlite3
import os
import json
import markdown
from database import create_connection, init_db, get_chords, get_chord, get_songs, get_song, get_lessons, get_lesson, get_user_progress, mark_lesson_complete
from math import ceil

app = Flask(__name__)
app.secret_key = 'guitar_master_secret_key'

# Инициализация базы данных при запуске
try:
    if not os.path.exists('guitar_tutor.db'):
        print("Создание новой базы данных...")
        init_db(create_new=True)
    else:
        print("Инициализация существующей базы данных...")
        init_db(create_new=False)
    print("База данных успешно инициализирована")
except Exception as e:
    print(f"Ошибка инициализации БД: {str(e)}")
    try:
        # Попытка восстановления
        if os.path.exists('guitar_tutor.db'):
            os.rename('guitar_tutor.db', 'guitar_tutor_corrupted.db')
        init_db(create_new=True)
        print("База данных восстановлена")
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")

# Константы пагинации
PER_PAGE = 5

# Маршруты
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chords')
def chords_page():
    page = request.args.get('page', 1, type=int)
    chords = get_chords()
    total_pages = ceil(len(chords) / PER_PAGE)
    start_idx = (page - 1) * PER_PAGE
    end_idx = start_idx + PER_PAGE
    paginated_chords = chords[start_idx:end_idx]
    
    return render_template('chords.html', 
                           chords=paginated_chords, 
                           current_page=page,
                           total_pages=total_pages)

@app.route('/chord/<name>')
def chord_image(name):
    return generate_chord_svg(name), 200, {'Content-Type': 'image/svg+xml'}

@app.route('/songs')
def songs_page():
    page = request.args.get('page', 1, type=int)
    songs = get_songs()
    total_pages = ceil(len(songs) / PER_PAGE)
    start_idx = (page - 1) * PER_PAGE
    end_idx = start_idx + PER_PAGE
    paginated_songs = songs[start_idx:end_idx]
    
    return render_template('songs.html', 
                           songs=paginated_songs, 
                           current_page=page,
                           total_pages=total_pages)

@app.route('/song/<int:song_id>')
def song_detail(song_id):
    song = get_song(song_id)
    if song:
        # Форматируем текст песни здесь
        formatted_lyrics = format_song_lyrics(song['lyrics'])
        return render_template('song_detail.html', 
                              song=song, 
                              formatted_lyrics=formatted_lyrics)
    return render_template('404.html'), 404

@app.route('/strumming')
def strumming_pattern():
    pattern = request.args.get('pattern', '↓ ↑ ↓ ↑')
    return generate_strumming_pattern(pattern), 200, {'Content-Type': 'image/svg+xml'}

@app.route('/lessons')
def lessons_page():
    lessons = get_lessons()
    user_id = session.get('user_id', 'default_user')
    completed_lessons = get_user_progress(user_id)
    total_lessons = len(lessons)
    
    # Рассчитываем процент завершения
    progress_percent = 0
    if total_lessons > 0:
        progress_percent = int(round(len(completed_lessons) / total_lessons * 100))
    
    return render_template(
        'lessons.html',
        lessons=lessons,
        completed_lessons=completed_lessons,
        progress_percent=progress_percent
    )

@app.route('/lesson/<int:lesson_id>')
def lesson_detail(lesson_id):
    lesson = get_lesson(lesson_id)
    if lesson:
        user_id = session.get('user_id', 'default_user')
        completed_lessons = get_user_progress(user_id)
        return render_template('lesson_detail.html', 
                              lesson=lesson, 
                              user_id=user_id,
                              completed_lessons=completed_lessons)
    return render_template('404.html'), 404

@app.route('/complete_lesson', methods=['POST'])
def complete_lesson():
    data = request.json
    user_id = session.get('user_id', 'default_user')
    lesson_id = data.get('lesson_id')
    
    if lesson_id:
        mark_lesson_complete(user_id, lesson_id)
        return jsonify({'success': True})
    
    return jsonify({'success': False}), 400

@app.route('/practice')
def practice():
    return render_template('practice.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Генератор аккордов
def generate_chord_svg(chord_name):
    chord = get_chord(chord_name)
    if not chord:
        return f'<svg width="200" height="250"><text x="100" y="125" text-anchor="middle">Аккорд не найден</text></svg>'
    
    try:
        positions = json.loads(chord['positions'])
    except:
        positions = []
    
    width = 200
    height = 250
    string_count = 6
    fret_count = 5
    margin = 20
    diagram_width = width - 2 * margin
    diagram_height = height - 2 * margin - 30
    
    # Начало SVG
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    
    # Фон
    svg += f'<rect width="100%" height="100%" fill="#f8f9fa" rx="10"/>'
    
    # Название аккорда
    svg += f'<text x="{width//2}" y="25" text-anchor="middle" font-size="18" font-weight="bold" fill="#2c3e50">{chord_name}</text>'
    
    # Гриф
    svg += f'<rect x="{margin}" y="{margin+10}" width="{diagram_width}" height="{diagram_height}" fill="#f5deb3" stroke="#8b4513" stroke-width="2" rx="5"/>'
    
    # Струны
    string_spacing = diagram_width / (string_count - 1)
    for i in range(string_count):
        x = margin + i * string_spacing
        stroke_width = 1 if i in [0, 5] else 0.5
        svg += f'<line x1="{x}" y1="{margin+10}" x2="{x}" y2="{margin+10+diagram_height}" stroke="#333" stroke-width="{stroke_width}"/>'
    
    # Лады
    fret_spacing = diagram_height / fret_count
    for i in range(fret_count + 1):
        y = margin + 10 + i * fret_spacing
        stroke_width = 2 if i == 0 else 1
        svg += f'<line x1="{margin}" y1="{y}" x2="{margin+diagram_width}" y2="{y}" stroke="#8b4513" stroke-width="{stroke_width}"/>'
    
    # Пальцы
    for pos in positions:
        fret = pos.get('fret', 0)
        if pos.get('barre'):
            # Баррэ
            start_string = min([p.get('string', 0) for p in positions if p.get('barre')])
            end_string = max([p.get('string', 0) for p in positions if p.get('barre')])
            x1 = margin + (6 - start_string) * string_spacing
            x2 = margin + (6 - end_string) * string_spacing
            y = margin + 10 + (fret - 0.5) * fret_spacing
            svg += f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="black" stroke-width="10" stroke-linecap="round"/>'
        elif fret > 0:
            # Обычный палец
            string_idx = 6 - pos.get('string', 0)
            x = margin + string_idx * string_spacing
            y = margin + 10 + (fret - 0.5) * fret_spacing
            svg += f'<circle cx="{x}" cy="{y}" r="8" fill="black"/>'
    
    # Открытые струны
    for i in range(1, 7):
        if not any(pos.get('string', 0) == i and pos.get('fret', 0) > 0 for pos in positions):
            x = margin + (6 - i) * string_spacing
            y = margin + 15
            svg += f'<text x="{x}" y="{y}" text-anchor="middle" font-size="14" fill="green">O</text>'
    
    # Заглушенные струны
    for pos in positions:
        if pos.get('muted'):
            x = margin + (6 - pos.get('string', 0)) * string_spacing
            y = margin + 15
            svg += f'<text x="{x}" y="{y}" text-anchor="middle" font-size="14" fill="red">X</text>'
    
    svg += '</svg>'
    return svg

# Генератор боёв
def generate_strumming_pattern(pattern):
    symbols = {
        '↓': 'M10,20 L40,50 M25,30 L25,30',
        '↑': 'M10,50 L40,20 M25,40 L25,40',
        'x': 'M10,20 L40,50 M10,50 L40,20',
        ' ': 'M25,35 L25,35',
        '>': 'M10,35 L30,35 L20,25 M30,35 L20,45',
        '~': 'M10,35 C20,25 30,25 40,35'
    }
    
    width = 400
    height = 120
    items = pattern.split()
    item_count = len(items)
    item_width = width / item_count if item_count > 0 else 0
    
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    svg += f'<rect width="100%" height="100%" fill="#f8f9fa" rx="10"/>'
    svg += f'<text x="10" y="25" font-size="16" font-weight="bold" fill="#2c3e50">Бой: {pattern}</text>'
    svg += f'<line x1="0" y1="50" x2="{width}" y2="50" stroke="#ddd" stroke-dasharray="5,5"/>'
    
    for i in range(item_count + 1):
        x = i * item_width
        svg += f'<line x1="{x}" y1="40" x2="{x}" y2="{height-20}" stroke="#eee"/>'
    
    for i, symbol in enumerate(items):
        x_center = (i + 0.5) * item_width
        y_center = 80
        
        if symbol in symbols:
            path = symbols[symbol]
            color = "#e74c3c" if symbol == '>' else "#3498db"
            svg += f'<path d="{path}" transform="translate({x_center-25},{y_center-35})" stroke="{color}" stroke-width="3" fill="none" stroke-linecap="round"/>'
        
        svg += f'<text x="{x_center}" y="{height-5}" text-anchor="middle" font-size="12" fill="#7f8c8d">{i+1}</text>'
    
    svg += '<path d="M0,50 '
    for i, symbol in enumerate(items):
        x = (i + 0.5) * item_width
        if symbol == '↓':
            svg += f'L{x},70 '
        elif symbol == '↑':
            svg += f'L{x},30 '
        else:
            svg += f'L{x},50 '
    svg += f'L{width},50" stroke="#2c3e50" stroke-width="2" fill="none"/>'
    
    svg += '</svg>'
    return svg

# Регистрация фильтров
@app.template_filter('markdown')
def markdown_filter(text):
    return markdown.markdown(text)

@app.template_filter('format_lyrics')
def format_lyrics_filter(text):
    return format_song_lyrics(text)

@app.template_filter('count_chords')
def count_chords_filter(chords_str):
    """Подсчитывает количество аккордов в строке"""
    if not chords_str:
        return 0
    return len(chords_str.split(','))

# Форматирование текста песен
def format_song_lyrics(lyrics):
    if not lyrics:
        return ""
    
    # Простой и безопасный метод
    lines = lyrics.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Заменяем [аккорд] на span с классом
        new_line = line.replace('[', '<span class="chord">').replace(']', '</span>')
        formatted_lines.append(f'<div class="song-line">{new_line}</div>')
    
    return ''.join(formatted_lines)

if __name__ == '__main__':
    app.run(debug=True)