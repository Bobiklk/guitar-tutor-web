document.addEventListener('DOMContentLoaded', function() {
    // Завершение урока
    const completeButtons = document.querySelectorAll('#complete-lesson');
    completeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const lessonId = this.dataset.lessonId;
            
            fetch('/complete_lesson', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ lesson_id: lessonId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.innerHTML = '<i class="fas fa-check"></i> Урок завершен';
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-success');
                    this.disabled = true;
                    
                    // Обновление статуса
                    const statusElement = document.querySelector('.completed-badge');
                    if (statusElement) {
                        statusElement.innerHTML = '<i class="fas fa-check-circle"></i> Завершено';
                    }
                }
            });
        });
    });
    
    // Таймер практики
    const startTimer = document.getElementById('start-timer');
    const pauseTimer = document.getElementById('pause-timer');
    const resetTimer = document.getElementById('reset-timer');
    const timerDisplay = document.querySelector('.timer-display');
    
    if (startTimer && timerDisplay) {
        let timerInterval;
        let minutes = 20;
        let seconds = 0;
        let isRunning = false;
        
        function updateDisplay() {
            timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        startTimer.addEventListener('click', function() {
            if (!isRunning) {
                isRunning = true;
                startTimer.innerHTML = '<i class="fas fa-pause"></i> Пауза';
                
                timerInterval = setInterval(() => {
                    if (seconds === 0) {
                        if (minutes === 0) {
                            clearInterval(timerInterval);
                            timerDisplay.textContent = "00:00";
                            startTimer.disabled = true;
                            return;
                        }
                        minutes--;
                        seconds = 59;
                    } else {
                        seconds--;
                    }
                    updateDisplay();
                }, 1000);
            } else {
                isRunning = false;
                startTimer.innerHTML = '<i class="fas fa-play"></i> Продолжить';
                clearInterval(timerInterval);
            }
        });
        
        pauseTimer?.addEventListener('click', function() {
            if (isRunning) {
                isRunning = false;
                startTimer.innerHTML = '<i class="fas fa-play"></i> Продолжить';
                clearInterval(timerInterval);
            }
        });
        
        resetTimer.addEventListener('click', function() {
            clearInterval(timerInterval);
            isRunning = false;
            minutes = 20;
            seconds = 0;
            updateDisplay();
            startTimer.innerHTML = '<i class="fas fa-play"></i> Старт';
            startTimer.disabled = false;
        });
        
        updateDisplay();
    }
    
    // Фильтры аккордов
    const chordSearch = document.getElementById('chord-search');
    if (chordSearch) {
        chordSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const chords = document.querySelectorAll('.chord-card');
            
            chords.forEach(chord => {
                const chordName = chord.dataset.name.toLowerCase();
                if (chordName.includes(searchTerm)) {
                    chord.style.display = 'block';
                } else {
                    chord.style.display = 'none';
                }
            });
        });
    }
    
    // Вкладки уроков
    const tabBtns = document.querySelectorAll('.tab-btn');
    if (tabBtns.length) {
        tabBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // Убрать активный класс у всех кнопок
                tabBtns.forEach(b => b.classList.remove('active'));
                // Добавить активный класс текущей кнопке
                this.classList.add('active');
                
                const tabType = this.dataset.tab;
                const lessons = document.querySelectorAll('.lesson-card');
                
                lessons.forEach(lesson => {
                    if (tabType === 'all') {
                        lesson.style.display = 'block';
                    } else {
                        if (lesson.dataset.type === tabType) {
                            lesson.style.display = 'block';
                        } else {
                            lesson.style.display = 'none';
                        }
                    }
                });
            });
        });
    }
});