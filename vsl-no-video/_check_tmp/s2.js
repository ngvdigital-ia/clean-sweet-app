// FAQ Accordion
        document.querySelectorAll('.faq-question').forEach(q => {
            q.addEventListener('click', () => {
                const item = q.parentElement;
                const answer = q.nextElementSibling;
                const isActive = item.classList.contains('active');
                document.querySelectorAll('.faq-item').forEach(i => {
                    i.classList.remove('active');
                    i.querySelector('.faq-answer').style.maxHeight = null;
                });
                if (!isActive) {
                    item.classList.add('active');
                    answer.style.maxHeight = answer.scrollHeight + 'px';
                }
            });
        });

        // Countdown Timer (15 minutes loop)
        function startCountdown() {
            var totalSeconds = 15 * 60;
            var saved = sessionStorage.getItem('cs_countdown');
            if (saved) {
                var elapsed = Math.floor((Date.now() - parseInt(saved)) / 1000);
                totalSeconds = Math.max(0, 15 * 60 - elapsed);
            } else {
                sessionStorage.setItem('cs_countdown', Date.now().toString());
            }
            function tick() {
                var m = Math.floor(totalSeconds / 60);
                var s = totalSeconds % 60;
                document.getElementById('minutes').textContent = m < 10 ? '0' + m : m;
                document.getElementById('seconds').textContent = s < 10 ? '0' + s : s;
                if (totalSeconds > 0) { totalSeconds--; setTimeout(tick, 1000); }
            }
            tick();
        }
        startCountdown();