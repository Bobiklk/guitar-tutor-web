import sqlite3
import os
import json

def create_connection():
    try:
        conn = sqlite3.connect('guitar_tutor.db', check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

def init_db(create_new=False):
    conn = create_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        # Проверяем существование таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Создаем таблицы, если их нет
        if 'chords' not in tables:
            cursor.execute('''
            CREATE TABLE chords (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                positions TEXT NOT NULL,
                difficulty INTEGER DEFAULT 1
            )
            ''')
        
        if 'songs' not in tables:
            cursor.execute('''
            CREATE TABLE songs (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                artist TEXT,
                chords TEXT,
                lyrics TEXT,
                strumming_pattern TEXT,
                difficulty INTEGER DEFAULT 2
            )
            ''')
        
        if 'lessons' not in tables:
            cursor.execute('''
            CREATE TABLE lessons (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                lesson_type TEXT,
                order_index INTEGER
            )
            ''')
        else:
            # Проверяем наличие столбца order_index
            cursor.execute("PRAGMA table_info(lessons)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'order_index' not in columns:
                print("Добавляем столбец order_index")
                cursor.execute("ALTER TABLE lessons ADD COLUMN order_index INTEGER")
                conn.commit()
        
        if 'user_progress' not in tables:
            cursor.execute('''
            CREATE TABLE user_progress (
                user_id TEXT,
                lesson_id INTEGER,
                completed BOOLEAN,
                completed_at DATETIME,
                PRIMARY KEY (user_id, lesson_id)
            )
            ''')
        
        # Проверяем наличие данных
        cursor.execute("SELECT COUNT(*) FROM chords")
        if cursor.fetchone()[0] == 0 or create_new:
            insert_test_data(cursor)
            print("Тестовые данные добавлены")
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Ошибка инициализации БД: {e}")
        return False
    finally:
        if conn:
            conn.close()

def insert_test_data(cursor):
    # Аккорды
    chords = [
        ('C', '[{"string":5,"fret":3},{"string":4,"fret":2},{"string":2,"fret":1}]', 1),
        ('G', '[{"string":6,"fret":3},{"string":5,"fret":2},{"string":1,"fret":3}]', 2),
        ('D', '[{"string":4,"fret":0},{"string":3,"fret":2},{"string":2,"fret":3},{"string":1,"fret":2}]', 2),
        ('Am', '[{"string":4,"fret":2},{"string":3,"fret":2},{"string":2,"fret":1}]', 1),
        ('Em', '[{"string":5,"fret":2},{"string":4,"fret":2}]', 1),
        ('F', '[{"string":6,"fret":1,"barre":1},{"string":5,"fret":3},{"string":4,"fret":3},{"string":3,"fret":2},{"string":2,"fret":1},{"string":1,"fret":1,"barre":1}]', 3),
        ('E', '[{"string":6,"fret":0},{"string":5,"fret":2},{"string":4,"fret":2},{"string":3,"fret":1},{"string":2,"fret":0},{"string":1,"fret":0}]', 2),
        ('A', '[{"string":5,"fret":0},{"string":4,"fret":2},{"string":3,"fret":2},{"string":2,"fret":2},{"string":1,"fret":0}]', 2),
        ('Dm', '[{"string":4,"fret":0},{"string":3,"fret":2},{"string":2,"fret":3},{"string":1,"fret":1}]', 2),
        ('Bm', '[{"string":5,"fret":2,"barre":2},{"string":4,"fret":4},{"string":3,"fret":4},{"string":2,"fret":4},{"string":1,"fret":2,"barre":2}]', 4),
        ('Cm', '[{"string":5,"fret":3},{"string":4,"fret":5},{"string":3,"fret":5},{"string":2,"fret":4}]', 3),
        ('G7', '[{"string":6,"fret":3},{"string":5,"fret":2},{"string":3,"fret":3},{"string":2,"fret":1},{"string":1,"fret":1}]', 3),
        ('Dsus4', '[{"string":4,"fret":0},{"string":3,"fret":2},{"string":2,"fret":3},{"string":1,"fret":3}]', 2),
        ('Asus2', '[{"string":5,"fret":0},{"string":4,"fret":2},{"string":3,"fret":2},{"string":2,"fret":0},{"string":1,"fret":0}]', 2),
        ('Fmaj7', '[{"string":4,"fret":3},{"string":3,"fret":2},{"string":2,"fret":1},{"string":1,"fret":0}]', 3),
        ('E7', '[{"string":6,"fret":0},{"string":5,"fret":2},{"string":4,"fret":1},{"string":3,"fret":0},{"string":2,"fret":0},{"string":1,"fret":0}]', 2),
        ('B7', '[{"string":5,"fret":2},{"string":4,"fret":1},{"string":3,"fret":2},{"string":2,"fret":0},{"string":1,"fret":2}]', 3),
        ('Cadd9', '[{"string":5,"fret":3},{"string":4,"fret":2},{"string":3,"fret":0},{"string":2,"fret":3},{"string":1,"fret":3}]', 3),
        ('Gm', '[{"string":6,"fret":3,"barre":3},{"string":5,"fret":5},{"string":4,"fret":5},{"string":3,"fret":4},{"string":2,"fret":3,"barre":3},{"string":1,"fret":3,"barre":3}]', 4),
        ('D7', '[{"string":4,"fret":0},{"string":3,"fret":2},{"string":2,"fret":1},{"string":1,"fret":2}]', 2)
    ]
    cursor.executemany('INSERT INTO chords (name, positions, difficulty) VALUES (?, ?, ?)', chords)
    
    # Песни с полными текстами
    songs = [
        ('Imagine', 'John Lennon', 'C,G,Am,F', 
         """[C]Imagine there's no [G]heaven
It's [Am]easy if you [F]try
[C]No hell below [G]us
[Am]Above us only [F]sky

[C]Imagine all the [G]people
[Am]Living for to[F]day
[C]Imagine there's no [G]countries
[Am]It isn't hard to [F]do
[C]Nothing to kill or [G]die for
[Am]And no religion [F]too
[C]Imagine all the [G]people
[Am]Living life in [F]peace

[Am]You may say [F]I'm a [G]dreamer
[C]But I'm not the only [F]one
[Am]I hope someday [F]you'll join [G]us
[C]And the world will be as [F]one

[C]Imagine no pos[G]sessions
[Am]I wonder if you [F]can
[C]No need for greed or [G]hunger
[Am]A brotherhood of [F]man
[C]Imagine all the [G]people
[Am]Sharing all the [F]world

[Am]You may say [F]I'm a [G]dreamer
[C]But I'm not the only [F]one
[Am]I hope someday [F]you'll join [G]us
[C]And the world will live as [F]one""", 
         "Down Down Up Up Down", 2),
         
        ('Knockin\' on Heaven\'s Door', 'Bob Dylan', 'G,D,Am,C', 
         """Mama take this [G]badge off of me
I can't use it [D]anymore
It's gettin' [Am]dark, too dark to [C]see
I feel like I'm [G]knockin' on heaven's [D]door

[Am]Knock, knock, knockin' on heaven's [C]door
[Am]Knock, knock, knockin' on heaven's [C]door
[Am]Knock, knock, knockin' on heaven's [C]door
[Am]Knock, knock, knockin' on heaven's [C]door

Mama put my [G]guns in the ground
I can't shoot them [D]anymore
That long black [Am]cloud is comin' [C]down
I feel like I'm [G]knockin' on heaven's [D]door""", 
         "Down Down Down Down", 2),
         
        ('Wonderwall', 'Oasis', 'Em,G,D,A', 
         """[Em]Today is gonna be the [G]day
That they're gonna [D]throw it back to [A]you
[Em]By now you should've [G]somehow
[D]Realized what you gotta [A]do

[Em]I don't believe that [G]anybody
[D]Feels the way I do about you [A]now

[Em]Backbeat the [G]word is on the [D]street
That the fire in your [A]heart is out
[Em]I'm sure you've heard it [G]all before
But you never really had a [D]doubt
I don't believe that [A]anybody
Feels the way I do about you [Em]now

And all the [G]roads we have to [D]walk are winding
And all the [A]lights that lead us there are blinding
There are many [Em]things that I would
[G]Like to say to you
[D]But I don't know [A]how

Because [Em]maybe
[G]You're gonna be the one that [D]saves me
[A]And after all
[Em]You're my wonder[G]wall""", 
         "Down Up Down Up", 3),
         
        ('Horse with No Name', 'America', 'Em,D6/9', 
         """[Em]On the first part of the journey
I was looking at all the [D6/9]life
[Em]There were plants and birds and rocks and [D6/9]things
There was sand and hills and [Em]rings
The first thing I met was a fly with a [D6/9]buzz
And the sky with no [Em]clouds
The heat was hot and the ground was [D6/9]dry
But the air was full of [Em]sound

I've been through the [D6/9]desert on a horse with no [Em]name
It felt good to be out of the [D6/9]rain
In the [Em]desert you can remember your [D6/9]name
'Cause there ain't no one for to give you no [Em]pain
La la la la la [D6/9]la
La la la la la [Em]la""", 
         "Down Down Down Down", 1),
         
        ('Zombie', 'The Cranberries', 'Em,C,G,D', 
         """[Em]Another head hangs [C]lowly
[G]Child is slowly [D]taken
[Em]And the violence [C]caused such [G]silence
Who are we [D]mistaken?

But you see it's not [Em]me
It's not my [C]family
In your [G]head, in your [D]head, they are [Em]fighting
With their [C]tanks and their [G]bombs
And their [D]bombs and their [Em]guns
In your [C]head, in your [G]head they are [D]crying

[Em]In your [C]head, in your [G]head
[D]Zombie, [Em]zombie, [C]zombie
[G]Ie, [D]ie, [Em]ie, [C]ie
[G]What's in your [D]head?
In your [Em]head? [C]Zombie, [G]zombie, [D]zombie""", 
         "Down Down Down Down Down Down", 3),
         
        ('House of the Rising Sun', 'Animals', 'Am,C,D,F,Em', 
         """[Am]There is a house in New [C]Orleans
They [D]call the Rising [F]Sun
And [Em]it's been the ruin of many a poor [Am]boy
And [C]God I [D]know I'm [F]one

[Am]My mother was a tailor
[C]Sewed my new blue jeans
[D]My father was a gamblin' [F]man
[Em]Down in New Or[Am]leans

[Am]Now the only thing a gambler [C]needs
Is a [D]suitcase and a [F]trunk
And [Em]the only time he's satisfied
Is [Am]when he's on a [C]drunk""", 
         "Down Down Up Up Down", 3),
         
        ('Let It Be', 'The Beatles', 'C,G,Am,F', 
         """[C]When I find myself in times of [G]trouble
Mother [Am]Mary comes to [F]me
[C]Speaking words of [G]wisdom
[Am]Let it [F]be

And [C]in my hour of [G]darkness
She is [Am]standing right in [F]front of me
[C]Speaking words of [G]wisdom
[Am]Let it [F]be

[C]Let it [G]be, let it [Am]be, let it [F]be, let it [C]be
[G]Whisper words of [Am]wisdom
[F]Let it [C]be""", 
         "Down Down Up Up Down", 2),
         
        ('Bad Moon Rising', 'Creedence', 'D,A,G', 
         """[D]I see the bad moon [A]arising
I see [G]trouble on the way
[D]I see earthquakes and [A]lightnin'
I see [G]bad times today

[D]Don't go around tonight
[A]Well, it's bound to take your life
[G]There's a bad moon on the rise

[D]I hear hurricanes a-blowing
[A]I know the end is coming soon
[G]I fear rivers over flowing
[D]I hear the voice of rage and ruin""", 
         "Down Down Up Up", 2),
         
        ('Sweet Home Alabama', 'Lynyrd Skynyrd', 'D,C,G', 
         """[D]Big wheels keep on turning
[C]Carry me home to see my [G]kin
[D]Singing songs about the [C]Southland
I miss [G]Alabamy once again
And I think it's a [D]sin, yes

[D]Well I heard Mister Young sing about her
[C]Well, I heard ole Neil put her [G]down
[D]Well, I hope Neil Young will remember
A [C]Southern man don't need him [G]around anyhow

[D]Sweet home [C]Alabama
[G]Where the skies are so blue
[D]Sweet home [C]Alabama
[G]Lord, I'm coming home to you""", 
         "Down Down Down Down", 3),
         
        ('Wish You Were Here', 'Pink Floyd', 'Em,G,Am,C,D', 
         """[Em]So, so you think you can [G]tell
[Am]Heaven from [C]Hell
[Em]Blue skies from [G]pain
[Am]Can you tell a green [C]field
[D]From a cold steel rail?
[Em]A smile from a [G]veil?
[Am]Do you think you can [C]tell?

And [Em]did they get you to [G]trade
[Am]Your heroes for [C]ghosts?
[Em]Hot ashes for [G]trees?
[Am]Hot air for a [C]cool breeze?
[D]Cold comfort for change?
And [Em]did you exchange
A [G]walk on part in the war
[Am]For a lead role in a [C]cage?

How I [Em]wish, how I [G]wish you were [Am]here
We're just two [C]lost souls [D]swimming in a fish [Em]bowl
Year after [G]year
Running over the same old [Am]ground
What have we [C]found?
The same old [D]fears
[Em]Wish you were [G]here""", 
         "Down Down Up Up Down", 4)
    ]
    cursor.executemany('INSERT INTO songs (title, artist, chords, lyrics, strumming_pattern, difficulty) VALUES (?, ?, ?, ?, ?, ?)', songs)
    
    # Уроки
    lessons = [
        ('Знакомство с гитарой', '## Основные части гитары\n- Гриф\n- Корпус\n- Головка грифа\n- Колки\n- Струны\n- Лады\n\n## Как держать гитару\nПравильная посадка очень важна для комфортной игры. Сидите прямо, гитара лежит на правой ноге (для правшей).', 'theory', 1),
        ('Настройка гитары', '## Стандартный строй\nСтруны настраиваются следующим образом:\n1. E (Ми) - самая тонкая\n2. B (Си)\n3. G (Соль)\n4. D (Ре)\n5. A (Ля)\n6. E (Ми) - самая толстая\n\nИспользуйте тюнер или приложение для настройки.', 'theory', 2),
        ('Постановка рук', '## Левая рука\n- Большой палец на середине грифа сзади\n- Пальцы округлены, нажимают подушечками\n- Не зажимайте струну слишком сильно\n\n## Правая рука\nРасслабленная кисть, движения от запястья', 'practice', 3),
        ('Первый аккорд: Em', '## Схема аккорда Em\n```\n0---|\n0---|\n0---|\n2---|  Безымянный палец\n2---|  Средний палец\n0---|\n```\n\n**Упражнение:** Ставим аккорд Em, медленно проводим по всем струнам.', 'practice', 4),
        ('Второй аккорд: Am', '## Схема аккорда Am\n```\n0---|\n1---|  Указательный палец\n2---|  Средний палец\n2---|  Безымянный палец\n0---|\n0---|\n```\n\n**Упражнение:** Переход между Em и Am. Считайте: 1-2-3-4 на каждом аккорде.', 'practice', 5),
        ('Простой бой', '## Паттерн: ↓ ↓ ↑ ↑ ↓\n\n- ↓ - движение кисти вниз\n- ↑ - движение кисти вверх\n\n**Счет:** 1 и 2 и 3 и 4 и\n**Движения:** ↓ (1) ↓ (и) ↑ (2) ↑ (и) ↓ (3) ↓ (и) ↑ (4) ↑ (и)', 'practice', 6),
        ('Аккорд C', '## Схема аккорда C\n```\n0---|\n1---|  Указательный палец\n0---|\n2---|  Средний палец\n3---|  Безымянный палец\nX---|  Не играем 6-ю струну\n```\n\n**Упражнение:** Переход между Am и C. Отрабатывайте плавность.', 'practice', 7),
        ('Играем первый куплет', '**Аккорды:** Em - Am - C\n\n```\n[Em]Сегодня будет [Am]дождь,\n[С]Сегодня будет [Em]гроза...\n```\n\nИграйте бой: ↓ ↓ ↑ ↑ ↓ для каждого аккорда. Меняйте аккорд на каждом такте.', 'practice', 8),
        ('Теория: Длительности нот', '## Основные длительности\n- Целая нота (4 доли)\n- Половинная (2 доли)\n- Четвертная (1 доля)\n- Восьмая (1/2 доли)\n\n**Ритмический рисунок:**\n♪ ♩ ♪ ♩ | ♪ ♪ ♩', 'theory', 9),
        ('Баррэ: Аккорд F', '## Схема аккорда F\n```\n1---|  Указательный палец (баррэ)\n1---|\n2---|  Средний палец\n3---|  Безымянный палец\n3---|  Мизинец\n1---|\n```\n\n**Совет:** Начинайте с частичного баррэ на первых двух струнах.', 'practice', 10),
        ('Перебор "Восьмерка"', '## Паттерн перебора\nСтруны: 4-3-2-3-1-3-2-3\n\n**Упражнение:** Играйте на аккорде Am:\n- Большой палец: 4-я струна\n- Указательный: 3-я\n- Средний: 2-я\n- Безымянный: 1-я', 'practice', 11),
        ('Песня "Пачка сигарет"', '**Аккорды:** Am, G, F, E\n\n```\n[Am]Я больше не курю,\n[G]И не пью за стойкой [F]бара,\n[E]Но все еще люблю,\n[Am]Как любил и [G]раньше, [F]даром...\n```\n\nБой: ↓ ↑ ↓ ↑', 'practice', 12),
        ('Теория: Тональности', '## Основные тональности\n- C (До мажор)\n- G (Соль мажор)\n- D (Ре мажор)\n- A (Ля мажор)\n- E (Ми мажор)\n\n**Квинтовый круг:**\nC → G → D → A → E → B → F# → C#', 'theory', 13),
        ('Импровизация: Пентатоника', '## Пентатоника в ля миноре\n```\nE|----------------5-8--\nB|------------5-8------\nG|--------5-7----------\nD|----5-7--------------\nA|--5-7----------------\nE|----------------------\n```\n\n**Упражнение:** Играйте ноты последовательно под аккорды Am, Dm, Em.', 'practice', 14),
        ('Завершение курса', 'Поздравляем! Вы освоили базовые навыки игры на гитаре.\n\n**Дальнейшие шаги:**\n1. Учите новые аккорды\n2. Разбирайте любимые песни\n3. Играйте с метрономом\n4. Найдите группу для совместной игры\n\nУдачи в вашем музыкальном пути!', 'theory', 15)
    ]
    cursor.executemany('INSERT INTO lessons (title, content, lesson_type, order_index) VALUES (?, ?, ?, ?)', lessons)

def get_chords():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, difficulty FROM chords ORDER BY name")
        chords = [{'id': row[0], 'name': row[1], 'difficulty': row[2]} for row in cursor.fetchall()]
        return chords
    except sqlite3.Error as e:
        print(f"Ошибка при получении аккордов: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_chord(name):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chords WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'positions': row[2],
                'difficulty': row[3]
            }
        return None
    except sqlite3.Error as e:
        print(f"Ошибка при получении аккорда {name}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_songs():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, artist, chords, difficulty FROM songs ORDER BY title")
        songs = []
        for row in cursor.fetchall():
            songs.append({
                'id': row[0],
                'title': row[1],
                'artist': row[2],
                'chords': row[3],
                'difficulty': row[4]
            })
        return songs
    except sqlite3.Error as e:
        print(f"Ошибка при получении песен: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_song(song_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'artist': row[2],
                'chords': row[3],
                'lyrics': row[4],
                'strumming_pattern': row[5],
                'difficulty': row[6]
            }
        return None
    except sqlite3.Error as e:
        print(f"Ошибка при получении песни {song_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_lessons():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lessons ORDER BY order_index")
        lessons = []
        for row in cursor.fetchall():
            lessons.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'lesson_type': row[3],
                'order_index': row[4]
            })
        return lessons
    except sqlite3.Error as e:
        print(f"Ошибка при получении уроков: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_lesson(lesson_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'lesson_type': row[3],
                'order_index': row[4]
            }
        return None
    except sqlite3.Error as e:
        print(f"Ошибка при получении урока {lesson_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_user_progress(user_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT lesson_id FROM user_progress WHERE user_id = ? AND completed = 1", (user_id,))
        completed_lessons = [row[0] for row in cursor.fetchall()]
        return completed_lessons
    except sqlite3.Error as e:
        print(f"Ошибка при получении прогресса: {e}")
        return []
    finally:
        if conn:
            conn.close()

def mark_lesson_complete(user_id, lesson_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_progress (user_id, lesson_id, completed, completed_at)
            VALUES (?, ?, 1, datetime('now'))
        ''', (user_id, lesson_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Ошибка при сохранении прогресса: {e}")
        return False
    finally:
        if conn:
            conn.close()