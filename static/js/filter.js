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

    // --- MAKALE BEĞENİ SİSTEMİ ---
    const likeBtn = document.getElementById('like-btn');
    if (likeBtn) {
        likeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const btn = this;
            const articleId = btn.getAttribute('data-article-id');
            const icon = document.getElementById('like-icon');
            const text = document.getElementById('like-text');
            const countSpan = document.getElementById('like-count');
            const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

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
                if (countSpan) countSpan.innerText = data.count; 
                if (data.liked) {
                    btn.classList.replace('btn-outline-danger', 'btn-danger');
                    if (icon) icon.classList.replace('far', 'fas');
                    if (text) text.innerText = 'Beğenildi';
                } else {
                    btn.classList.replace('btn-danger', 'btn-outline-danger');
                    if (icon) icon.classList.replace('fas', 'far');
                    if (text) text.innerText = 'Beğen';
                }
            });
        });
    }

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

    // --- YORUM GÖNDERME (AJAX) ---
    const commentForm = document.querySelector('#comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const form = this;
            const formData = new FormData(form);
            const parentId = formData.get('parent_id');

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Yanıtsa sayfayı yenilemek en sağlıklısı (iç içe yapı karmaşıklığı için)
                    // Normal yorumsa başa ekleyebiliriz ama kullanıcı deneyimi için yenileme daha güvenli
                    if (parentId) {
                        location.reload();
                    } else {
                        // Eğer ana yorumsa ve sayfa yenilenmesin isteniyorsa buraya ekleme kodu gelebilir
                        // Ancak user "yanıt verilince yer değiştiriyor" dediği için reload en temiz çözüm.
                        location.reload();
                    }
                }
            });
        });
    }
});