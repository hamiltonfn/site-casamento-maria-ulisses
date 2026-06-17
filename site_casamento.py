import os
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configurações
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
PASSWORD = 'maria123'   # Altere a senha aqui

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- HTML embutido (template) ----------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Maria & Ulisses · Galeria</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700&display=swap" rel="stylesheet" />
    <style>
        /* ---------- RESET & BASE ---------- */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: #f7f2ed;
            color: #2d241f;
            line-height: 1.5;
            padding-bottom: 2rem;
        }
        :root {
            --gold: #c9a87c;
            --gold-light: #e6d4b5;
            --gold-gradient: linear-gradient(135deg, #d4b48c, #b8936a);
            --cream: #fcf8f4;
            --shadow-soft: 0 15px 40px rgba(0,0,0,0.06), 0 5px 15px rgba(0,0,0,0.04);
            --shadow-hover: 0 25px 50px rgba(0,0,0,0.12), 0 8px 20px rgba(0,0,0,0.06);
            --radius-card: 20px;
            --radius-btn: 50px;
            --transition: 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        /* ---------- HEADER ---------- */
        .hero {
            text-align: center;
            padding: 3.5rem 1.5rem 2.5rem;
            background: var(--cream);
            position: relative;
            border-bottom: 1px solid rgba(201, 168, 124, 0.2);
        }
        .hero::after {
            content: '';
            position: absolute;
            bottom: -1px;
            left: 0;
            width: 100%;
            height: 3px;
            background: var(--gold-gradient);
        }
        .hero .ornament {
            font-size: 1.8rem;
            color: var(--gold);
            letter-spacing: 12px;
            opacity: 0.6;
        }
        .hero h1 {
            font-family: 'Great Vibes', cursive;
            font-size: 4.2rem;
            font-weight: 400;
            color: #3d2c26;
            margin: 0.2rem 0 0.1rem;
            text-shadow: 0 2px 10px rgba(201, 168, 124, 0.15);
        }
        .hero .date {
            font-size: 1.05rem;
            font-weight: 400;
            color: #8a7468;
            letter-spacing: 3px;
            background: rgba(255,255,255,0.6);
            backdrop-filter: blur(6px);
            display: inline-block;
            padding: 0.3rem 2rem;
            border-radius: 40px;
            border: 1px solid rgba(201,168,124,0.25);
            margin-top: 0.2rem;
        }
        .hero p {
            max-width: 520px;
            margin: 0.9rem auto 0;
            font-weight: 300;
            color: #6a5a4e;
            font-size: 0.95rem;
            letter-spacing: 0.3px;
        }

        /* ---------- UPLOAD & ACTIONS ---------- */
        .toolbar {
            max-width: 1300px;
            margin: 1.8rem auto 0.5rem;
            padding: 0 1.5rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem 1.2rem;
            align-items: center;
            justify-content: space-between;
        }
        .upload-group {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            align-items: center;
            background: white;
            padding: 0.4rem 0.8rem 0.4rem 1.2rem;
            border-radius: var(--radius-btn);
            box-shadow: var(--shadow-soft);
            border: 1px solid rgba(201,168,124,0.15);
        }
        .upload-group input[type="file"] {
            font-size: 0.85rem;
            color: #4d3e36;
            cursor: pointer;
            border: none;
            background: transparent;
            padding: 0.3rem 0;
            max-width: 200px;
        }
        .upload-group input[type="file"]::file-selector-button {
            background: var(--gold-gradient);
            color: white;
            border: none;
            padding: 0.4rem 1.2rem;
            border-radius: 40px;
            font-weight: 600;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
            margin-right: 0.8rem;
        }
        .upload-group input[type="file"]::file-selector-button:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 12px rgba(201,168,124,0.3);
        }
        .upload-group button {
            background: var(--gold-gradient);
            color: white;
            border: none;
            padding: 0.5rem 1.6rem;
            border-radius: var(--radius-btn);
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 4px 12px rgba(201,168,124,0.25);
        }
        .upload-group button:hover {
            transform: scale(1.03);
            box-shadow: 0 6px 18px rgba(201,168,124,0.35);
        }

        .actions-group {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            align-items: center;
        }
        .actions-group button {
            background: white;
            border: 1px solid #dcd0c8;
            padding: 0.5rem 1.4rem;
            border-radius: var(--radius-btn);
            font-weight: 500;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.25s;
            color: #3d2c26;
            box-shadow: var(--shadow-soft);
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .actions-group button:hover {
            border-color: var(--gold);
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
        }
        .actions-group button#deleteSelectedBtn {
            background: #e74c3c;
            color: white;
            border-color: #e74c3c;
        }
        .actions-group button#deleteSelectedBtn:hover {
            background: #c0392b;
            border-color: #c0392b;
        }
        .actions-group button#deleteSelectedBtn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
            transform: none;
        }
        #selectedCount {
            font-size: 0.85rem;
            color: #6a5a4e;
            font-weight: 500;
            min-width: 100px;
        }

        /* ---------- GALERIA ---------- */
        .gallery-container {
            max-width: 1300px;
            margin: 1.5rem auto 0;
            padding: 0 1.5rem;
        }
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1.5rem;
        }
        .gallery-item {
            position: relative;
            border-radius: var(--radius-card);
            overflow: hidden;
            background: white;
            box-shadow: var(--shadow-soft);
            transition: all var(--transition);
            aspect-ratio: 1 / 1;
            cursor: pointer;
            will-change: transform;
        }
        .gallery-item:hover {
            transform: translateY(-8px);
            box-shadow: var(--shadow-hover);
        }
        .gallery-item img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.6s ease;
        }
        .gallery-item:hover img {
            transform: scale(1.04);
        }
        .gallery-item .heart-overlay {
            position: absolute;
            bottom: 14px;
            right: 18px;
            font-size: 1.3rem;
            color: rgba(255,255,255,0.7);
            text-shadow: 0 2px 12px rgba(0,0,0,0.2);
            opacity: 0;
            transition: opacity 0.4s;
            pointer-events: none;
        }
        .gallery-item:hover .heart-overlay {
            opacity: 1;
        }

        /* Checkbox de seleção - estilo moderno */
        .select-checkbox {
            position: absolute;
            top: 14px;
            left: 14px;
            z-index: 10;
            width: 22px;
            height: 22px;
            cursor: pointer;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.25s;
            accent-color: var(--gold);
            transform: scale(1.1);
        }
        .select-checkbox.visible {
            opacity: 1;
            pointer-events: auto;
        }
        .selection-mode .select-checkbox {
            opacity: 1 !important;
            pointer-events: auto !important;
        }

        /* Botão deletar individual - minimalista */
        .delete-btn {
            position: absolute;
            top: 14px;
            right: 14px;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(6px);
            color: white;
            border: none;
            border-radius: 50%;
            width: 34px;
            height: 34px;
            font-size: 18px;
            line-height: 34px;
            text-align: center;
            cursor: pointer;
            transition: all 0.25s;
            z-index: 10;
            opacity: 0;
            pointer-events: none;
            font-weight: 300;
            box-shadow: 0 2px 10px rgba(0,0,0,0.15);
        }
        .gallery-item:hover .delete-btn {
            opacity: 1;
            pointer-events: auto;
        }
        .delete-btn:hover {
            background: #e74c3c;
            transform: scale(1.08);
        }
        .selection-mode .delete-btn {
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* ---------- LIGHTBOX PREMIUM ---------- */
        .lightbox {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(20, 15, 13, 0.92);
            backdrop-filter: blur(16px);
            z-index: 9999;
            justify-content: center;
            align-items: center;
            padding: 1.5rem;
            animation: fadeIn 0.35s ease;
        }
        .lightbox.active { display: flex; }
        .lightbox .lightbox-content {
            position: relative;
            max-width: 92vw;
            max-height: 88vh;
        }
        .lightbox img {
            max-width: 92vw;
            max-height: 88vh;
            border-radius: 16px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.5);
            object-fit: contain;
            border: 2px solid rgba(255,255,255,0.08);
        }
        .lightbox .close-btn {
            position: absolute;
            top: 20px;
            right: 30px;
            font-size: 2.6rem;
            color: rgba(255,255,255,0.6);
            cursor: pointer;
            background: none;
            border: none;
            transition: all 0.25s;
            z-index: 30;
        }
        .lightbox .close-btn:hover { color: #fff; transform: rotate(90deg); }
        .lightbox .counter {
            position: absolute;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255,255,255,0.5);
            font-size: 0.85rem;
            background: rgba(0,0,0,0.3);
            padding: 0.3rem 1.4rem;
            border-radius: 40px;
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255,255,255,0.05);
            letter-spacing: 1px;
        }
        .lightbox .nav-btn {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255,255,255,0.06);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255,255,255,0.08);
            color: rgba(255,255,255,0.6);
            font-size: 2.6rem;
            padding: 0.6rem 1.2rem;
            cursor: pointer;
            border-radius: 60px;
            transition: all 0.25s;
            z-index: 30;
        }
        .lightbox .nav-btn:hover {
            background: rgba(255,255,255,0.12);
            color: #fff;
            border-color: rgba(255,255,255,0.15);
        }
        .lightbox .prev { left: 16px; }
        .lightbox .next { right: 16px; }

        .lightbox .delete-lightbox-btn {
            position: absolute;
            bottom: 80px;
            right: 28px;
            background: rgba(231, 76, 60, 0.85);
            backdrop-filter: blur(8px);
            color: white;
            border: none;
            border-radius: 40px;
            padding: 0.6rem 1.6rem;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s;
            z-index: 30;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            letter-spacing: 0.3px;
        }
        .lightbox .delete-lightbox-btn:hover {
            background: #c0392b;
            transform: scale(1.04);
        }

        /* ---------- FOOTER ---------- */
        .footer {
            text-align: center;
            padding: 3rem 1rem 2rem;
            color: #6a5a4e;
            font-weight: 300;
            font-size: 0.9rem;
            border-top: 1px solid rgba(201,168,124,0.15);
            margin-top: 3rem;
        }
        .footer .hearts {
            color: #c0826a;
            font-size: 1.2rem;
            letter-spacing: 6px;
        }
        .footer small {
            display: block;
            margin-top: 0.5rem;
            opacity: 0.5;
            font-size: 0.75rem;
            letter-spacing: 0.5px;
        }

        /* ---------- FLASH MESSAGES ---------- */
        .flash-message {
            max-width: 700px;
            margin: 0.8rem auto;
            padding: 0.8rem 1.5rem;
            border-radius: 60px;
            font-weight: 500;
            text-align: center;
            background: #fff;
            box-shadow: var(--shadow-soft);
            border-left: 4px solid;
        }
        .flash-message.error {
            border-color: #e74c3c;
            color: #c0392b;
        }
        .flash-message.success {
            border-color: #27ae60;
            color: #1e8449;
        }

        /* ---------- ANIMAÇÕES ---------- */
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        @keyframes scaleUp {
            0% { transform: scale(0.92); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }
        .gallery-item {
            animation: scaleUp 0.4s ease both;
        }

        /* ---------- RESPONSIVE ---------- */
        @media (max-width: 768px) {
            .hero h1 { font-size: 3rem; }
            .gallery-grid { grid-template-columns: repeat(auto-fill, minmax(160px,1fr)); gap: 1rem; }
            .toolbar { flex-direction: column; align-items: stretch; }
            .upload-group { justify-content: center; padding: 0.6rem 1rem; }
            .upload-group input[type="file"] { max-width: 100%; }
            .actions-group { justify-content: center; }
            .lightbox .nav-btn { font-size: 2rem; padding: 0.3rem 0.8rem; }
            .lightbox .prev { left: 6px; }
            .lightbox .next { right: 6px; }
            .lightbox .delete-lightbox-btn { bottom: 70px; right: 50%; transform: translateX(50%); }
        }
        @media (max-width: 480px) {
            .hero h1 { font-size: 2.4rem; }
            .gallery-grid { grid-template-columns: repeat(auto-fill, minmax(130px,1fr)); gap: 0.8rem; }
        }
    </style>
</head>
<body>

    <!-- ===== HERO ===== -->
    <header class="hero">
        <div class="ornament">✦ ✧ ✦</div>
        <h1>Maria &amp; Ulisses</h1>
        <div class="date">• 11 · 07 · 2026 •</div>
        <p>Uma vida de amor começa com um sim. Reviva os momentos mais especiais do nosso grande dia.</p>
    </header>

    <!-- ===== FLASH MESSAGES ===== -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="flash-message {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <!-- ===== TOOLBAR ===== -->
    <div class="toolbar">
        <div class="upload-group">
            <form action="/upload" method="POST" enctype="multipart/form-data" style="display:flex; flex-wrap:wrap; gap:0.5rem; align-items:center;">
                <input type="file" name="photo" accept="image/*" multiple required />
                <button type="submit">➕ Adicionar</button>
            </form>
        </div>
        <div class="actions-group">
            <button id="toggleSelectBtn">☑ Selecionar</button>
            <button id="deleteSelectedBtn" disabled>🗑 Excluir</button>
            <span id="selectedCount"></span>
        </div>
    </div>

    <!-- ===== GALERIA ===== -->
    <section class="gallery-container">
        <div class="gallery-grid" id="galleryGrid">
            {% for img in images %}
            <div class="gallery-item" data-index="{{ loop.index0 }}" data-filename="{{ img }}">
                <img src="{{ url_for('static', filename='images/' + img) }}" alt="Foto do casamento" loading="lazy" />
                <div class="heart-overlay">❤</div>
                <input type="checkbox" class="select-checkbox" data-filename="{{ img }}" />
                <form action="/delete/{{ img }}" method="POST" class="delete-form" style="position:absolute; top:14px; right:14px; z-index:10; margin:0;">
                    <input type="hidden" name="password" value="" class="password-input" />
                    <button type="submit" class="delete-btn" onclick="return askPassword(this)">✕</button>
                </form>
            </div>
            {% else %}
            <p style="grid-column:1/-1; text-align:center; color:#8a7468; padding:4rem 0; font-weight:300;">Nenhuma foto ainda. Comece enviando as primeiras memórias ✨</p>
            {% endfor %}
        </div>
    </section>

    <!-- ===== LIGHTBOX ===== -->
    <div class="lightbox" id="lightbox">
        <button class="close-btn" id="closeLightbox">✕</button>
        <button class="nav-btn prev" id="prevBtn">‹</button>
        <button class="nav-btn next" id="nextBtn">›</button>
        <div class="lightbox-content">
            <img id="lightboxImg" src="" alt="Foto ampliada" />
            <form action="" method="POST" id="deleteLightboxForm">
                <input type="hidden" name="password" value="" class="password-input-lightbox" />
                <button type="submit" class="delete-lightbox-btn" onclick="return askPasswordLightbox(this)">🗑 Excluir</button>
            </form>
        </div>
        <span class="counter" id="counter"></span>
    </div>

    <!-- ===== FOOTER ===== -->
    <footer class="footer">
        <div class="hearts">❤ ❤ ❤</div>
        <p>Com todo carinho, Maria &amp; Ulisses</p>
        <small>Fotos eternizadas em 11 de julho de 2026</small>
    </footer>

    <!-- ===== SCRIPTS ===== -->
    <script>
        // ---------- SENHA (exclusão individual) ----------
        function askPassword(btn) {
            var form = btn.closest('form');
            var pwd = prompt('Digite a senha para excluir esta foto:');
            if (pwd === null) return false;
            form.querySelector('.password-input').value = pwd;
            return true;
        }
        function askPasswordLightbox(btn) {
            var form = btn.closest('form');
            var pwd = prompt('Digite a senha para excluir esta foto:');
            if (pwd === null) return false;
            form.querySelector('.password-input-lightbox').value = pwd;
            return true;
        }

        // ---------- SELEÇÃO MÚLTIPLA (sem botão "Cancelar") ----------
        (function() {
            const toggleBtn = document.getElementById('toggleSelectBtn');
            const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
            const selectedCountSpan = document.getElementById('selectedCount');
            const checkboxes = document.querySelectorAll('.select-checkbox');
            const galleryGrid = document.getElementById('galleryGrid');
            let selectionMode = false;

            function updateUI() {
                const checked = document.querySelectorAll('.select-checkbox:checked');
                const count = checked.length;
                if (count > 0) {
                    deleteSelectedBtn.disabled = false;
                    selectedCountSpan.textContent = `${count} selecionada(s)`;
                } else {
                    deleteSelectedBtn.disabled = true;
                    selectedCountSpan.textContent = '';
                }
            }

            function toggleSelection() {
                selectionMode = !selectionMode;
                galleryGrid.classList.toggle('selection-mode', selectionMode);
                // O botão mantém o mesmo texto, não muda para "Cancelar"
                if (!selectionMode) {
                    checkboxes.forEach(cb => cb.checked = false);
                    updateUI();
                }
            }

            toggleBtn.addEventListener('click', toggleSelection);
            checkboxes.forEach(cb => cb.addEventListener('change', updateUI));

            deleteSelectedBtn.addEventListener('click', function() {
                const checked = document.querySelectorAll('.select-checkbox:checked');
                if (checked.length === 0) return;
                const pwd = prompt('Digite a senha para excluir as fotos selecionadas:');
                if (pwd === null) return;
                const filenames = Array.from(checked).map(cb => cb.dataset.filename);

                fetch('/delete-multiple', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password: pwd, filenames: filenames })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) location.reload();
                    else alert('Erro: ' + data.message);
                })
                .catch(() => alert('Erro ao excluir. Tente novamente.'));
            });

            updateUI();
        })();

        // ---------- LIGHTBOX ----------
        (function() {
            const items = document.querySelectorAll('.gallery-item');
            const lightbox = document.getElementById('lightbox');
            const img = document.getElementById('lightboxImg');
            const close = document.getElementById('closeLightbox');
            const prev = document.getElementById('prevBtn');
            const next = document.getElementById('nextBtn');
            const counter = document.getElementById('counter');
            const deleteForm = document.getElementById('deleteLightboxForm');
            let current = 0;
            const total = items.length;

            function open(idx) {
                if (!total) return;
                current = (idx + total) % total;
                update();
                lightbox.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
            function closeLightbox() {
                lightbox.classList.remove('active');
                document.body.style.overflow = '';
            }
            function update() {
                const item = items[current];
                const filename = item.dataset.filename;
                img.src = item.querySelector('img').src;
                counter.textContent = `${current+1} / ${total}`;
                deleteForm.action = '/delete/' + filename;
                deleteForm.querySelector('.password-input-lightbox').value = '';
            }
            function prevImage() { if (total) { current = (current - 1 + total) % total; update(); } }
            function nextImage() { if (total) { current = (current + 1) % total; update(); } }

            items.forEach((item, idx) => {
                item.addEventListener('click', (e) => {
                    if (e.target.closest('.select-checkbox') || e.target.closest('.delete-btn') || e.target.closest('.delete-form')) return;
                    open(idx);
                });
            });

            close.addEventListener('click', closeLightbox);
            prev.addEventListener('click', (e) => { e.stopPropagation(); prevImage(); });
            next.addEventListener('click', (e) => { e.stopPropagation(); nextImage(); });

            document.addEventListener('keydown', (e) => {
                if (!lightbox.classList.contains('active')) return;
                if (e.key === 'Escape') closeLightbox();
                if (e.key === 'ArrowLeft') prevImage();
                if (e.key === 'ArrowRight') nextImage();
            });
            lightbox.addEventListener('click', (e) => { if (e.target === lightbox) closeLightbox(); });

            let touchX = 0;
            lightbox.addEventListener('touchstart', (e) => { touchX = e.changedTouches[0].screenX; }, { passive: true });
            lightbox.addEventListener('touchend', (e) => {
                const diff = touchX - e.changedTouches[0].screenX;
                if (Math.abs(diff) > 40) diff > 0 ? nextImage() : prevImage();
            }, { passive: true });
        })();
    </script>
</body>
</html>
"""

# ---------- ROTAS ----------
@app.route('/')
def index():
    images = sorted([f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)])
    return render_template_string(HTML_TEMPLATE, images=images)

@app.route('/upload', methods=['POST'])
def upload():
    if 'photo' not in request.files:
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('index'))
    files = request.files.getlist('photo')
    if not files or all(f.filename == '' for f in files):
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('index'))

    uploaded = 0
    skipped = 0
    for file in files:
        if file.filename == '':
            continue
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            base, ext = os.path.splitext(filename)
            cnt = 1
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                filename = f"{base}_{cnt}{ext}"
                cnt += 1
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploaded += 1
        else:
            skipped += 1

    if uploaded:
        flash(f'{uploaded} foto(s) adicionada(s) com sucesso!', 'success')
    if skipped:
        flash(f'{skipped} arquivo(s) ignorado(s) (formato inválido).', 'error')
    if not uploaded and not skipped:
        flash('Nenhum arquivo válido.', 'error')
    return redirect(url_for('index'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    pwd = request.form.get('password')
    if pwd != PASSWORD:
        flash('Senha incorreta.', 'error')
        return redirect(url_for('index'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        flash('Arquivo não encontrado.', 'error')
    return redirect(url_for('index'))

@app.route('/delete-multiple', methods=['POST'])
def delete_multiple():
    data = request.get_json()
    if not data or 'password' not in data or 'filenames' not in data:
        return jsonify({'success': False, 'message': 'Dados inválidos.'}), 400
    if data['password'] != PASSWORD:
        return jsonify({'success': False, 'message': 'Senha incorreta.'}), 403

    deleted = 0
    for filename in data['filenames']:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            deleted += 1
    return jsonify({'success': True, 'deleted': deleted})

@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)