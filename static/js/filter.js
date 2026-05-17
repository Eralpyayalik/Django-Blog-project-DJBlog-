document.addEventListener('DOMContentLoaded', function() {
    // --- KATEGORİ FİLTRELEME ---
    const buttons = document.querySelectorAll('.category-btn');
    const articles = document.querySelectorAll('.article-item');
    if (buttons.length > 0) {
        buttons.forEach(button => {
            button.addEventListener('click', function() {
                buttons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                const filter = this.getAttribute('data-filter');
                articles.forEach(article => {
                    article.style.opacity = '0';
                    article.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        if (filter === 'all' || article.getAttribute('data-category') === filter) {
                            article.classList.remove('d-none');
                            article.style.display = '';
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

    // --- MAKALE BEĞENİ SİSTEMİ (KALDIRILDI - detail.html İÇİNDE YÖNETİLİYOR) ---

    // --- YORUM BEĞENİ SİSTEMİ (DELEGATION) ---
    document.addEventListener('click', function(e) {
        if (e.target.closest('.comment-like-btn')) {
            const btn = e.target.closest('.comment-like-btn');
            const commentId = btn.getAttribute('data-comment-id');
            const icon = btn.querySelector('i');
            const countSpan = btn.querySelector('.like-count');
            const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            fetch(`/articles/comment/like/${commentId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': token,
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.liked) {
                    btn.classList.replace('text-muted', 'text-danger');
                    icon.classList.replace('far', 'fas');
                } else {
                    btn.classList.replace('text-danger', 'text-muted');
                    icon.classList.replace('fas', 'far');
                }
                countSpan.innerText = data.count;
            });
        }

        // --- YANITLARI GÖSTER/GİZLE ---
        if (e.target.closest('.toggle-replies-btn')) {
            const btn = e.target.closest('.toggle-replies-btn');
            const targetId = btn.getAttribute('data-target');
            const container = document.getElementById(targetId);
            const icon = btn.querySelector('i');

            if (container.classList.contains('d-none')) {
                container.classList.remove('d-none');
                btn.innerHTML = `<i class="fas fa-chevron-up me-1"></i> Yanıtları Gizle`;
            } else {
                container.classList.add('d-none');
                btn.innerHTML = `<i class="fas fa-chevron-down me-1"></i> Yanıtları Gör`;
            }
        }
    });


});