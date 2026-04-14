document.addEventListener('DOMContentLoaded', function() {
    // --- FİLTRELEME SİSTEMİ ---
    const buttons = document.querySelectorAll('.category-btn');
    if (buttons.length > 0) {
        buttons.forEach(button => {
            button.addEventListener('click', function() {
                document.querySelectorAll('.category-btn').forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');

                const filter = this.getAttribute('data-filter');
                const articles = document.querySelectorAll('.article-item');

                articles.forEach(article => {
                    article.style.opacity = '0';
                    article.style.transform = 'scale(0.9)';
                    
                    setTimeout(() => {
                        if (filter === 'all' || article.getAttribute('data-category') === filter) {
                            article.style.display = 'block';
                            setTimeout(() => {
                                article.style.opacity = '1';
                                article.style.transform = 'scale(1)';
                            }, 50);
                        } else {
                            article.style.display = 'none';
                        }
                    }, 300);
                });
            });
        });
    }

    // --- BEĞENİ SİSTEMİ ---
    const likeBtn = document.getElementById('like-btn');
    if (likeBtn) {
        likeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const btn = this;
            const articleId = btn.getAttribute('data-article-id');
            const icon = document.getElementById('like-icon');
            const text = document.getElementById('like-text');
            const countSpan = document.getElementById('like-count');

            const token = typeof csrftoken !== 'undefined' ? csrftoken : document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            fetch(`/articles/like/${articleId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': token,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (countSpan) countSpan.innerText = data.count || data.like_count; 
                if (data.liked) {
                    btn.classList.replace('btn-outline-danger', 'btn-danger');
                    if (icon) icon.classList.replace('far', 'fas');
                    if (text) text.innerText = 'Beğenildi';
                } else {
                    btn.classList.replace('btn-danger', 'btn-outline-danger');
                    if (icon) icon.classList.replace('fas', 'far');
                    if (text) text.innerText = 'Beğen';
                }
            })
            .catch(error => console.error('Hata:', error));
        });
    }

    // --- CKEDITOR CANLI OKUMA SÜRESİ (GÜVENLİ BAĞLANTI) ---
    if (typeof CKEDITOR !== 'undefined') {
        CKEDITOR.on('instanceReady', function(evt) {
            var editor = evt.editor;
            
            function updateLiveReadTime() {
                var data = editor.getData();
                var cleanText = data.replace(/<\/?[^>]+(>|$)/g, " ").replace(/&nbsp;/g, " ");
                var words = cleanText.trim().split(/\s+/);
                var wordCount = (cleanText.trim() === "") ? 0 : words.length;
                var readTime = Math.ceil(wordCount / 200) || 1;

                var badge = document.getElementById('live-read-time');
                if (badge) badge.innerText = readTime + " dk";
            }

            editor.on('change', updateLiveReadTime);
            editor.on('key', updateLiveReadTime);
            editor.on('paste', updateLiveReadTime);
        });
    }
}); 