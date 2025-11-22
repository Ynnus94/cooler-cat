/* CoolerCat Application Logic */

const API_BASE = 'http://localhost:5001/api';
let currentJobId = null;
let quoteInterval = null;

// --- Confetti Logic ---
class Confetti {
    constructor() {
        this.canvas = document.getElementById('confetti-canvas');
        if (!this.canvas) {
            this.canvas = document.createElement('canvas');
            this.canvas.id = 'confetti-canvas';
            document.body.appendChild(this.canvas);
        }
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticle(x, y) {
        const colors = ['#667eea', '#a855f7', '#06b6d4', '#f59e0b', '#10b981', '#ef4444'];
        return {
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 10,
            vy: (Math.random() - 0.5) * 10 - 5,
            size: Math.random() * 8 + 4,
            color: colors[Math.floor(Math.random() * colors.length)],
            rotation: Math.random() * 360,
            rotationSpeed: (Math.random() - 0.5) * 10,
            opacity: 1
        };
    }

    explode(x, y, count = 100) {
        for (let i = 0; i < count; i++) {
            this.particles.push(this.createParticle(x, y));
        }
        if (!this.animating) {
            this.animate();
        }
    }

    animate() {
        this.animating = true;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        for (let i = 0; i < this.particles.length; i++) {
            const p = this.particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.2; // Gravity
            p.rotation += p.rotationSpeed;
            p.opacity -= 0.01;

            this.ctx.save();
            this.ctx.translate(p.x, p.y);
            this.ctx.rotate(p.rotation * Math.PI / 180);
            this.ctx.globalAlpha = p.opacity;
            this.ctx.fillStyle = p.color;
            this.ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);
            this.ctx.restore();

            if (p.opacity <= 0 || p.y > this.canvas.height) {
                this.particles.splice(i, 1);
                i--;
            }
        }

        if (this.particles.length > 0) {
            requestAnimationFrame(() => this.animate());
        } else {
            this.animating = false;
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
    }
}

const confetti = new Confetti();


// --- Dark Mode Logic ---
function initDarkMode() {
    const toggle = document.createElement('div');
    toggle.className = 'theme-toggle';
    toggle.title = 'Toggle Dark Mode';
    document.body.appendChild(toggle);

    // Function to update icon based on current mode
    function updateIcon() {
        if (document.body.classList.contains('dark-mode')) {
            toggle.innerHTML = `
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
                </svg>
            `;
        } else {
            toggle.innerHTML = `
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                </svg>
            `;
        }
    }

    // Check local storage and apply dark mode
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }

    // Set initial icon
    updateIcon();

    // Toggle on click
    toggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
        updateIcon();
    });
}

// --- Custom Modal Functions ---
function showModal(title, message, type = 'alert', imageSrc = null) {
    return new Promise((resolve) => {
        const overlay = document.getElementById('modalOverlay');
        const modalTitle = document.getElementById('modalTitle');
        const modalMessage = document.getElementById('modalMessage');
        const modalFooter = document.getElementById('modalFooter');
        const modalImageContainer = document.getElementById('modalImageContainer');
        const modalImage = document.getElementById('modalImage');

        modalTitle.textContent = title;
        modalMessage.textContent = message;

        // Show/hide image
        if (imageSrc) {
            modalImage.src = imageSrc;
            modalImageContainer.style.display = 'flex';
        } else {
            modalImageContainer.style.display = 'none';
        }

        if (type === 'confirm') {
            modalFooter.innerHTML = `
                <button class="btn btn-secondary" id="modalCancelBtn">Cancel</button>
                <button class="btn btn-primary" id="modalConfirmBtn">Confirm</button>
            `;

            document.getElementById('modalCancelBtn').onclick = () => {
                overlay.style.display = 'none';
                resolve(false);
            };

            document.getElementById('modalConfirmBtn').onclick = () => {
                overlay.style.display = 'none';
                resolve(true);
            };
        } else {
            modalFooter.innerHTML = `
                <button class="btn btn-primary" id="modalConfirmBtn">OK</button>
            `;

            document.getElementById('modalConfirmBtn').onclick = () => {
                overlay.style.display = 'none';
                resolve(true);
            };
        }

        overlay.style.display = 'flex';

        // Close on overlay click
        overlay.onclick = (e) => {
            if (e.target === overlay) {
                overlay.style.display = 'none';
                if (type === 'alert') {
                    resolve(true);
                } else {
                    resolve(false);
                }
            }
        };

        // Close on Escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                overlay.style.display = 'none';
                document.removeEventListener('keydown', escapeHandler);
                if (type === 'alert') {
                    resolve(true);
                } else {
                    resolve(false);
                }
            }
        };
        document.addEventListener('keydown', escapeHandler);
    });
}

function showAlert(message, title = 'Alert', imageSrc = null) {
    return showModal(title, message, 'alert', imageSrc);
}

function showConfirm(message, imageSrc = null) {
    return showModal('Confirm', message, 'confirm', imageSrc);
}

// --- Loading & Quotes ---
const funnyQuotes = [
    "Translating translations... how meta!",
    "Revising revisions... we're going deep!",
    "Processing your XLF with extra care ✨",
    "Quality checking like a boss 🎯",
    "Finding all the typos... there are many!",
    "Applying French grammar rules... oui oui!",
    "Making translations great again!",
    "Counting words... 1, 2, beaucoup!",
    "Polishing your translations to perfection",
    "Almost there... just a few more seconds!",
    "Quality is not an act, it is a habit... processing!",
    "Translating with the power of AI magic 🪄",
    "Checking for anglicisms... found 42!",
    "Adding non-breaking spaces like a pro",
    "Revising with style guide precision"
];

function showLoading(text, subtext) {
    document.getElementById('loadingText').textContent = text;
    document.getElementById('loadingSubtext').textContent = subtext;
    document.getElementById('loadingOverlay').classList.add('active');

    // Rotate funny quotes every 3 seconds if processing
    if (text.includes('Processing') || text.includes('Reprocessing')) {
        let quoteIndex = 0;
        quoteInterval = setInterval(() => {
            quoteIndex = (quoteIndex + 1) % funnyQuotes.length;
            document.getElementById('loadingSubtext').textContent = funnyQuotes[quoteIndex];
        }, 3000);
    }
}

function hideLoading() {
    if (quoteInterval) {
        clearInterval(quoteInterval);
        quoteInterval = null;
    }
    document.getElementById('loadingOverlay').classList.remove('active');
}

// --- API Functions ---
async function uploadFile(file) {
    if (!file.name.endsWith('.xlf') && !file.name.endsWith('.xlf.xlf')) {
        await showAlert('Please upload a valid XLF file (.xlf or .xlf.xlf)');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showLoading('Uploading file...', 'Sending your XLF to the server...');

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minute timeout

        const response = await fetch(`${API_BASE}/jobs`, {
            method: 'POST',
            body: formData,
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            let errorMessage = 'Upload failed';
            try {
                const error = await response.json();
                errorMessage = error.error || errorMessage;
            } catch (e) {
                errorMessage = `Server error: ${response.status} ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }

        showLoading('Processing file...', funnyQuotes[0]);

        const result = await response.json();

        // Log stats if available (debug mode)
        if (result.stats) {
            if (window.DEBUG_MODE) console.log('Processing stats:', result.stats);
            const stats = result.stats;
            if (stats.total) {
                showLoading('Processing file...', `Found ${stats.total} translations...`);
            }
            if (stats.with_revisions) {
                showLoading('Processing file...', `Applied ${stats.with_revisions} revisions...`);
            }
        }

        await new Promise(resolve => setTimeout(resolve, 1500));

        hideLoading();
        await loadJobs();
        await openJob(result.job_id, result.name);

        // Confetti on successful upload/process
        confetti.explode(window.innerWidth / 2, window.innerHeight / 2);

    } catch (error) {
        hideLoading();
        if (error.name === 'AbortError') {
            await showAlert('Error: Request timed out. The file might be too large or processing is taking too long.');
        } else if (error.message.includes('Failed to fetch')) {
            await showAlert('Error: Cannot connect to server. Make sure the server is running:\n\ncd scripts && python3 server.py');
        } else {
            await showAlert('Error: ' + error.message);
        }
    }
}

async function loadJobs() {
    try {
        const response = await fetch(`${API_BASE}/jobs`);

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const jobs = await response.json();
        const jobsList = document.getElementById('jobsList');

        if (jobs.length === 0) {
            jobsList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📁</div>
                    <div class="empty-state-text">No jobs yet. Upload an XLF file to get started!</div>
                </div>
            `;
            return;
        }

        jobsList.innerHTML = jobs.map(job => `
            <div class="job-card" onclick="openJob('${job.id}', '${escapeHtml(job.name)}')">
                <div class="job-info">
                    <div class="job-name">${escapeHtml(job.name)}</div>
                    <div class="job-meta">Created: ${new Date(job.created).toLocaleString()}</div>
                </div>
                <div class="job-actions" onclick="event.stopPropagation()">
                    <button class="btn btn-accent" onclick="reviseJob('${job.id}')" title="AI-powered revision of all translations">
                        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                        </svg>
                        Revise
                    </button>
                    <button class="btn btn-secondary" onclick="reprocessJob('${job.id}')">Reprocess</button>
                    <button class="btn btn-danger" onclick="deleteJob('${job.id}')">Delete</button>
                </div>
            </div>
        `).join('');

        if (document.getElementById('tableView').style.display !== 'none' && currentJobId) {
            updateJobSelector(currentJobId);
        }

    } catch (error) {
        console.error('Error loading jobs:', error);
        document.getElementById('jobsList').innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <div class="empty-state-text" style="color: #ef4444; font-weight: 600; margin-bottom: 10px;">Server not running!</div>
                <div class="empty-state-text" style="font-size: 14px;">
                    Please start the server first:<br>
                    <code style="background: #f3f4f6; padding: 4px 8px; border-radius: 4px; margin-top: 8px; display: inline-block;">cd scripts && python3 server.py</code>
                </div>
            </div>
        `;
    }
}

async function openJob(jobId, jobName) {
    try {
        showLoading('Loading job data...', 'Fetching your translations...');

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minute timeout

        const response = await fetch(`${API_BASE}/jobs/${jobId}/data`, {
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            let errorMessage = 'Failed to load job data';
            try {
                const error = await response.json();
                errorMessage = error.error || errorMessage;
            } catch (e) {
                errorMessage = `Server error: ${response.status} ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();

        hideLoading();

        document.querySelector('.section:has(#uploadArea)').style.display = 'none';
        document.getElementById('jobsSection').style.display = 'none';
        document.getElementById('tableView').style.display = 'block';

        currentJobId = jobId;
        await updateJobSelector(jobId);
        renderTable(result.data, 'tableContainer');

    } catch (error) {
        hideLoading();
        if (error.name === 'AbortError') {
            await showAlert('Error: Request timed out. Processing might be taking longer than expected.');
        } else if (error.message.includes('Failed to fetch')) {
            await showAlert('Error: Cannot connect to server. Make sure the server is running.');
        } else {
            await showAlert('Error opening job: ' + error.message);
        }
    }
}

async function switchJob(jobId) {
    if (!jobId) return;
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}`);
        const job = await response.json();
        await openJob(jobId, job.name);
    } catch (error) {
        await showAlert('Error switching job: ' + error.message);
    }
}

async function updateJobSelector(selectedJobId) {
    const selector = document.getElementById('jobSelector');
    const jobs = await fetch(`${API_BASE}/jobs`).then(r => r.json());

    selector.innerHTML = '<option value="">Select a job...</option>';
    jobs.forEach(job => {
        const option = document.createElement('option');
        option.value = job.id;
        option.textContent = job.name;
        option.selected = job.id === selectedJobId;
        selector.appendChild(option);
    });
}

function showJobsList() {
    document.getElementById('tableView').style.display = 'none';
    document.querySelector('.section:has(#uploadArea)').style.display = 'block';
    document.getElementById('jobsSection').style.display = 'block';
    currentJobId = null;
}

async function reviseJob(jobId) {
    const confirmed = await showConfirm(
        'Start AI-powered revision? I will review each translation segment individually using my knowledge and your resources. This may take several minutes.',
        'assets/surprisedcat.webp'
    );
    if (!confirmed) {
        return;
    }

    // Show progress bar instead of modal
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const progressPercent = document.getElementById('progress-percent');

    if (progressContainer) {
        progressContainer.style.display = 'block';
        progressBar.style.width = '0%';
        progressText.textContent = 'Initializing AI...';
        progressPercent.textContent = '0%';
    }

    // Start polling for progress
    const pollInterval = setInterval(async () => {
        try {
            const progressRes = await fetch(`${API_BASE}/jobs/${jobId}/progress`);
            if (progressRes.ok) {
                const progress = await progressRes.json();
                if (progress.percentage !== undefined && progressContainer) {
                    progressBar.style.width = `${progress.percentage}%`;
                    progressText.textContent = progress.message || 'Processing...';
                    progressPercent.textContent = `${progress.percentage}%`;
                }
            }
        } catch (e) {
            console.error('Error polling progress:', e);
        }
    }, 1000); // Poll every second

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 1800000); // 30 minute timeout

        const response = await fetch(`${API_BASE}/jobs/${jobId}/revise`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({}),
            signal: controller.signal
        });

        clearTimeout(timeoutId);
        clearInterval(pollInterval); // Stop polling

        if (!response.ok) {
            let errorMessage = 'AI revision failed';
            try {
                const error = await response.json();
                errorMessage = error.error || errorMessage;
            } catch (e) {
                errorMessage = `Server error: ${response.status} ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();

        // Update progress to 100%
        if (progressContainer) {
            progressBar.style.width = '100%';
            progressText.textContent = 'Complete!';
            progressPercent.textContent = '100%';

            // Hide after a delay
            setTimeout(() => {
                progressContainer.style.display = 'none';
            }, 2000);
        }

        await new Promise(resolve => setTimeout(resolve, 1000));

        // Confetti Celebration!
        confetti.explode(window.innerWidth / 2, window.innerHeight / 2, 200);

        const stats = result.stats || {};
        const revisedCount = stats.revised || 0;
        const totalCount = stats.total || 0;
        await showAlert(
            `AI revision completed!\n\nRevised: ${revisedCount} out of ${totalCount} segments`,
            'Success',
            'assets/proudcat.webp'
        );

        await loadJobs();
        await openJob(jobId, null);

    } catch (error) {
        clearInterval(pollInterval); // Stop polling on error
        if (progressContainer) progressContainer.style.display = 'none';

        if (error.name === 'AbortError') {
            await showAlert('Error: Request timed out. AI revision might be taking longer than expected.');
        } else if (error.message.includes('Failed to fetch')) {
            await showAlert('Error: Cannot connect to server. Make sure the server is running.');
        } else {
            await showAlert('Error during AI revision: ' + error.message);
        }
    }
}


async function reprocessJob(jobId) {
    const confirmed = await showConfirm('Reprocess this job? This will regenerate the revision table and HTML.', 'assets/sadcat.webp');
    if (!confirmed) {
        return;
    }

    showLoading('Reprocessing job...', funnyQuotes[0]);

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minute timeout

        const response = await fetch(`${API_BASE}/jobs/${jobId}/process`, {
            method: 'POST',
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            let errorMessage = 'Reprocessing failed';
            try {
                const error = await response.json();
                errorMessage = error.error || errorMessage;
            } catch (e) {
                errorMessage = `Server error: ${response.status} ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();

        await new Promise(resolve => setTimeout(resolve, 1000));

        hideLoading();
        await loadJobs();
        await openJob(jobId, null);

    } catch (error) {
        hideLoading();
        if (error.name === 'AbortError') {
            await showAlert('Error: Request timed out. Processing might be taking longer than expected.');
        } else if (error.message.includes('Failed to fetch')) {
            await showAlert('Error: Cannot connect to server. Make sure the server is running.');
        } else {
            await showAlert('Error: ' + error.message);
        }
    }
}

async function deleteJob(jobId) {
    const confirmed = await showConfirm('Are you sure you want to delete this job? This action cannot be undone.', 'assets/surprisedcat.webp');
    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Delete failed');
        }

        loadJobs();

    } catch (error) {
        await showAlert('Error: ' + error.message);
    }
}

// --- Utility Functions ---
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTextWithTags(text) {
    if (!text) return '';
    const tagPattern = /(<[^>]+>|<\/[^>]+>)/g;
    const parts = text.split(tagPattern);
    const formattedParts = [];
    for (const part of parts) {
        if (tagPattern.test(part)) {
            if (part.startsWith('</')) {
                formattedParts.push(`<span class="tag tag-closing">${escapeHtml(part)}</span>`);
            } else {
                formattedParts.push(`<span class="tag">${escapeHtml(part)}</span>`);
            }
        } else {
            if (part.trim()) {
                formattedParts.push(`<span class="text-content">${escapeHtml(part)}</span>`);
            } else {
                formattedParts.push(escapeHtml(part));
            }
        }
    }
    return formattedParts.join('');
}

function highlightDifferences(original, revised) {
    if (!original || !revised) return formatTextWithTags(revised || original);
    if (original === revised) return formatTextWithTags(revised);

    // Remove tags for comparison but keep track of their positions
    const tagPattern = /(<[^>]+>|<\/[^>]+>)/g;
    const originalClean = original.replace(tagPattern, ' ').replace(/\s+/g, ' ').trim();
    const revisedClean = revised.replace(tagPattern, ' ').replace(/\s+/g, ' ').trim();

    if (originalClean === revisedClean) return formatTextWithTags(revised);

    // Get formatted version first (with tags preserved)
    let formatted = formatTextWithTags(revised);
    
    // Better approach: compare word by word positionally
    const originalWords = originalClean.toLowerCase().split(/\s+/).filter(w => w.length > 0);
    const revisedWords = revisedClean.split(/\s+/).filter(w => w.length > 0);
    const originalWordsLower = originalWords.map(w => w.toLowerCase());
    
    // Find words that are different or in different positions
    const wordsToHighlight = [];
    const maxLen = Math.max(originalWords.length, revisedWords.length);
    
    for (let i = 0; i < revisedWords.length; i++) {
        const revWord = revisedWords[i];
        const revWordLower = revWord.toLowerCase();
        
        // Check if word exists at same position in original
        let foundAtPosition = false;
        if (i < originalWordsLower.length && originalWordsLower[i] === revWordLower) {
            foundAtPosition = true;
        }
        
        // If not at same position, check if it exists elsewhere nearby
        if (!foundAtPosition) {
            let foundNearby = false;
            const searchRange = 3;
            const start = Math.max(0, i - searchRange);
            const end = Math.min(originalWordsLower.length, i + searchRange + 1);
            
            for (let j = start; j < end; j++) {
                if (originalWordsLower[j] === revWordLower) {
                    foundNearby = true;
                    break;
                }
            }
            
            // If word doesn't exist nearby or is in different position, highlight it
            if (!foundNearby || !foundAtPosition) {
                wordsToHighlight.push({
                    word: revWord,
                    wordLower: revWordLower,
                    index: i
                });
            }
        }
    }
    
    // Also check for completely new words
    const originalWordsSet = new Set(originalWordsLower);
    for (let i = 0; i < revisedWords.length; i++) {
        const revWordLower = revisedWords[i].toLowerCase();
        if (!originalWordsSet.has(revWordLower) && revWordLower.length > 1) {
            // Check if not already in wordsToHighlight
            const alreadyAdded = wordsToHighlight.some(w => w.index === i);
            if (!alreadyAdded) {
                wordsToHighlight.push({
                    word: revisedWords[i],
                    wordLower: revWordLower,
                    index: i
                });
            }
        }
    }
    
    if (wordsToHighlight.length === 0) return formatted;
    
    // Sort by index descending to apply highlights from end to start
    wordsToHighlight.sort((a, b) => b.index - a.index);
    
    // Extract text content for matching (without HTML tags)
    const textContent = formatted.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().toLowerCase();
    
    // Apply highlights - use a simpler approach: find and replace in formatted text
    for (const { word, wordLower } of wordsToHighlight) {
        // Find the word in the text content
        let searchIndex = 0;
        const positions = [];
        
        while (true) {
            const index = textContent.indexOf(wordLower, searchIndex);
            if (index === -1) break;
            
            // Check word boundaries
            const before = index > 0 ? textContent[index - 1] : ' ';
            const after = index + wordLower.length < textContent.length ? textContent[index + wordLower.length] : ' ';
            if ((/\s/.test(before) || /[^\w]/.test(before)) && (/\s/.test(after) || /[^\w]/.test(after))) {
                positions.push(index);
            }
            searchIndex = index + 1;
        }
        
        // Apply highlights from end to start
        for (let posIdx = positions.length - 1; posIdx >= 0; posIdx--) {
            const textPos = positions[posIdx];
            
            // Find corresponding position in formatted HTML by counting characters
            let charCount = 0;
            let startPos = -1;
            let endPos = -1;
            
            for (let i = 0; i < formatted.length; i++) {
                if (formatted[i] === '<') {
                    // Skip HTML tags
                    const tagEnd = formatted.indexOf('>', i);
                    if (tagEnd !== -1) {
                        i = tagEnd;
                        continue;
                    }
                } else {
                    if (charCount === textPos && startPos === -1) {
                        startPos = i;
                    }
                    if (startPos !== -1 && charCount < textPos + word.length) {
                        endPos = i + 1;
                    }
                    charCount++;
                }
            }
            
            if (startPos !== -1 && endPos !== -1) {
                // Check if already highlighted
                const beforeText = formatted.substring(Math.max(0, startPos - 50), startPos);
                if (!beforeText.includes('diff-added')) {
                    const matchText = formatted.substring(startPos, endPos);
                    // Don't highlight if it's already inside a diff span
                    if (!matchText.includes('diff-added') && !matchText.includes('<span')) {
                        formatted = formatted.substring(0, startPos) + 
                            `<span class="diff-added">${matchText}</span>` + 
                            formatted.substring(endPos);
                    }
                }
            }
        }
    }

    return formatted;
}

function base64ToUtf8(base64) {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    const decoder = new TextDecoder('utf-8');
    return decoder.decode(bytes);
}

function copyToClipboard(button) {
    const textB64 = button.getAttribute('data-text-b64');
    let text = base64ToUtf8(textB64);
    const tempDiv = document.createElement('div');
    tempDiv.textContent = text;
    text = tempDiv.textContent || text;

    navigator.clipboard.writeText(text).then(function () {
        const originalText = button.innerHTML;
        button.innerHTML = `
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            Copied!
        `;
        button.classList.add('copied');
        setTimeout(function () {
            button.innerHTML = originalText;
            button.classList.remove('copied');
        }, 2000);
    }).catch(async function (err) {
        console.error('Failed to copy: ', err);
        await showAlert('Failed to copy to clipboard');
    });
}

function copyCommentToClipboard(button) {
    const textB64 = button.getAttribute('data-text-b64');
    let text = base64ToUtf8(textB64);
    const tempDiv = document.createElement('div');
    tempDiv.textContent = text;
    text = tempDiv.textContent || text;

    navigator.clipboard.writeText(text).then(function () {
        const originalText = button.innerHTML;
        button.innerHTML = `
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            Copied!
        `;
        button.classList.add('copied');
        setTimeout(function () {
            button.innerHTML = originalText;
            button.classList.remove('copied');
        }, 2000);
    }).catch(async function (err) {
        console.error('Failed to copy: ', err);
        await showAlert('Failed to copy to clipboard');
    });
}

function editRevision(button) {
    const matecatId = button.getAttribute('data-matecat-id');
    const textDiv = document.getElementById('text-' + matecatId);
    const textarea = document.getElementById('textarea-' + matecatId);
    const editButton = button;
    const saveButton = button.parentElement.querySelector('.save-button');
    const cancelButton = button.parentElement.querySelector('.cancel-button');
    const copyButton = button.parentElement.querySelector('.copy-button');

    if (!textDiv || !textarea) return;

    textDiv.classList.add('editing');
    textarea.classList.add('editing');
    editButton.style.display = 'none';
    saveButton.style.display = 'inline-flex';
    cancelButton.style.display = 'inline-flex';
    copyButton.style.display = 'none';
    textarea.focus();
    textarea.setSelectionRange(textarea.value.length, textarea.value.length);
}

function saveRevision(button) {
    const matecatId = button.getAttribute('data-matecat-id');
    const textDiv = document.getElementById('text-' + matecatId);
    const textarea = document.getElementById('textarea-' + matecatId);
    const editButton = button.parentElement.querySelector('.edit-button');
    const saveButton = button;
    const cancelButton = button.parentElement.querySelector('.cancel-button');
    const copyButton = button.parentElement.querySelector('.copy-button');
    const badge = document.getElementById('badge-' + matecatId);

    if (!textDiv || !textarea) return;

    const newText = textarea.value;
    
    // Check if it's an AI revision or XLF revision
    const isAiRevision = matecatId.includes('-ai');
    const isXlfRevision = matecatId.includes('-xlf');
    
    // Get the original target for comparison
    let originalTarget = '';
    const baseMatecatId = matecatId.replace(/-ai$/, '').replace(/-xlf$/, '');
    const row = document.querySelector(`tr[data-matecat-id="${baseMatecatId}"]`);
    if (row) {
        const targetCell = row.querySelector('.target-col');
        if (targetCell && targetCell.dataset.rawTarget) {
            originalTarget = targetCell.dataset.rawTarget;
        }
    }
    
    // Highlight differences if we have original target
    let formattedText;
    if (originalTarget && (isAiRevision || isXlfRevision)) {
        formattedText = highlightDifferences(originalTarget, newText);
    } else {
        formattedText = formatTextWithTags(newText);
    }
    
    const badgeHtml = isAiRevision ? '<span class="ai-badge">AI</span>' : '';
    textDiv.innerHTML = formattedText + badgeHtml + '<span class="edited-badge">EDITED</span>';
    textDiv.classList.remove('editing');
    textarea.classList.remove('editing');

    if (badge) badge.style.display = 'inline-block';
    localStorage.setItem('revision_' + matecatId, newText);

    const newTextB64 = btoa(unescape(encodeURIComponent(newText)));
    copyButton.setAttribute('data-text-b64', newTextB64);

    editButton.style.display = 'inline-flex';
    saveButton.style.display = 'none';
    cancelButton.style.display = 'none';
    copyButton.style.display = 'inline-flex';

    const originalText = button.innerHTML;
    button.innerHTML = `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
        </svg>
        Saved!
    `;
    setTimeout(function () {
        button.innerHTML = originalText;
    }, 1500);
}

function cancelEdit(button) {
    const matecatId = button.getAttribute('data-matecat-id');
    const textDiv = document.getElementById('text-' + matecatId);
    const textarea = document.getElementById('textarea-' + matecatId);
    const editButton = button.parentElement.querySelector('.edit-button');
    const saveButton = button.parentElement.querySelector('.save-button');
    const cancelButton = button;
    const copyButton = button.parentElement.querySelector('.copy-button');

    if (!textDiv || !textarea) return;

    const originalB64 = textarea.getAttribute('data-original-b64');
    const savedText = localStorage.getItem('revision_' + matecatId);
    const textToShow = savedText || atob(originalB64);

    const badge = document.getElementById('badge-' + matecatId);
    const isAiRevision = matecatId.includes('-ai');
    const isXlfRevision = matecatId.includes('-xlf');
    const badgeHtml = isAiRevision ? '<span class="ai-badge">AI</span>' : '';
    
    // Get the original target for comparison
    let originalTarget = '';
    const baseMatecatId = matecatId.replace(/-ai$/, '').replace(/-xlf$/, '');
    const row = document.querySelector(`tr[data-matecat-id="${baseMatecatId}"]`);
    if (row) {
        const targetCell = row.querySelector('.target-col');
        if (targetCell && targetCell.dataset.rawTarget) {
            originalTarget = targetCell.dataset.rawTarget;
        }
    }
    
    // Highlight differences if we have original target
    let formattedText;
    if (originalTarget && (isAiRevision || isXlfRevision)) {
        formattedText = highlightDifferences(originalTarget, textToShow);
    } else {
        formattedText = formatTextWithTags(textToShow);
    }
    
    if (savedText && badge) {
        textDiv.innerHTML = formattedText + badgeHtml + '<span class="edited-badge">EDITED</span>';
        badge.style.display = 'inline-block';
    } else {
        textDiv.innerHTML = formattedText + badgeHtml;
        if (badge) badge.style.display = 'none';
    }

    textarea.value = textToShow;
    textDiv.classList.remove('editing');
    textarea.classList.remove('editing');
    editButton.style.display = 'inline-flex';
    saveButton.style.display = 'none';
    cancelButton.style.display = 'none';
    copyButton.style.display = 'inline-flex';
}

function getConfidenceColor(score) {
    score = parseInt(score) || 0;
    if (score >= 90) return '#10b981'; // Green
    if (score >= 70) return '#f59e0b'; // Orange
    return '#ef4444'; // Red
}

// --- Table Rendering & Filtering ---
function renderTable(rows, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const total = rows.length;
    const withXlfRevisions = rows.filter(r => r['New target']?.trim()).length;
    const withAiRevisions = rows.filter(r => r['AI Revision']?.trim()).length;
    const withRevisions = withXlfRevisions + withAiRevisions;
    const withCodes = rows.filter(r => r['Code']?.trim()).length;
    const majorErrors = rows.filter(r => r['Code']?.includes('TE-2')).length;

    const statsHtml = `
        <div class="stats">
            <div class="stat-box" data-filter="all" onclick="applyStatFilter('all')">
                <h3>${total}</h3>
                <p>Total Translations</p>
            </div>
            <div class="stat-box ai-revisions" data-filter="ai-revisions" onclick="applyStatFilter('ai-revisions')">
                <h3>${withAiRevisions}</h3>
                <p>AI Revisions ✨</p>
            </div>
            <div class="stat-box xlf-revisions" data-filter="xlf-revisions" onclick="applyStatFilter('xlf-revisions')">
                <h3>${withXlfRevisions}</h3>
                <p>Revision</p>
            </div>
            <div class="stat-box warning" data-filter="error-codes" onclick="applyStatFilter('error-codes')">
                <h3>${withCodes}</h3>
                <p>With Error Codes</p>
            </div>
            <div class="stat-box major-errors ${majorErrors > 0 ? 'has-errors' : ''}" data-filter="major-errors" onclick="applyStatFilter('major-errors')">
                <h3>${majorErrors}</h3>
                <p>Major Errors (TE-2)</p>
            </div>
        </div>
    `;

    const filtersHtml = `
        <div class="filter-controls">
            <div class="filter-group">
                <label for="codeFilter">Filter by Code</label>
                <select id="codeFilter" onchange="filterTable()">
                    <option value="">All Codes</option>
                    <option value="TE-2">TE-2 (Major Translation Error)</option>
                    <option value="TE-0.5">TE-0.5 (Minor Translation Error)</option>
                    <option value="TC-0.5">TC-0.5 (Terminology/Consistency)</option>
                    <option value="LQ-0.5">LQ-0.5 (Language Quality)</option>
                    <option value="ST-0.5">ST-0.5 (Style)</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="stateFilter">Filter by State</label>
                <select id="stateFilter" onchange="filterTable()">
                    <option value="">All States</option>
                    <option value="translated">Translated</option>
                    <option value="reviewed">Reviewed</option>
                    <option value="final">Final</option>
                    <option value="draft">Draft</option>
                    <option value="new">New</option>
                </select>
            </div>
            <div class="filter-group id-range-group">
                <label>ID Range</label>
                <input type="number" id="idRangeMin" placeholder="Min (e.g. 4778127503)" oninput="filterTable()">
                <input type="number" id="idRangeMax" placeholder="Max (e.g. 4778127875)" oninput="filterTable()">
            </div>
            <div class="filter-group">
                <label for="searchBox">Search</label>
                <input type="text" id="searchBox" placeholder="Search in source, target, or revision..." oninput="filterTable()">
            </div>
        </div>
    `;

    let tableRowsHtml = '';
    for (const row of rows) {
        const matecatId = escapeHtml(row['ID Matecat'] || '');
        const state = (row['State'] || '').toLowerCase();
        const sourceRaw = row['Source'] || '';
        const targetRaw = row['Target'] || '';
        const newTargetRaw = row['New target'] || '';
        const aiRevisionRaw = row['AI Revision'] || '';
        const confidenceScore = row['Confidence Score'] || '';
        const code = escapeHtml(row['Code'] || '');
        const comment = escapeHtml(row['Comment'] || '');

        const source = formatTextWithTags(sourceRaw);
        const target = formatTextWithTags(targetRaw);
        const newTarget = formatTextWithTags(newTargetRaw);
        const aiRevision = formatTextWithTags(aiRevisionRaw);

        const hasAnyRevision = newTargetRaw || aiRevisionRaw;
        const hasAiRevision = !!aiRevisionRaw;
        const rowClass = hasAnyRevision ? 'has-revision' : 'no-revision';
        const hasRevision = hasAnyRevision ? 'true' : 'false';
        const hasAiRevisionAttr = hasAiRevision ? 'true' : 'false';

        let codeHtml = '';
        if (code) {
            const codes = code.split(',').map(c => c.trim());
            codeHtml = codes.map(c => {
                const cssClass = `code-${c.replace(/\./g, '').replace(/-/g, '')}`;
                return `<span class="${cssClass}">${c}</span>`;
            }).join(' ');
        }

        let stateBadge = '<span style="color: #94a3b8;">—</span>';
        if (state) {
            stateBadge = `<span class="state-badge state-${state}">${state}</span>`;
        }

        let commentDisplay = '';
        if (comment) {
            const commentB64 = btoa(unescape(encodeURIComponent(comment)));
            commentDisplay = `
                <div class="comment-wrapper">
                    <div>${comment}</div>
                    <button class="comment-copy-button" data-text-b64="${commentB64}" onclick="copyCommentToClipboard(this)" title="Copy comment">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                        </svg>
                        Copy
                    </button>
                </div>
            `;
        }

        let newTargetDisplay = '<em>No revision</em>';
        if (newTargetRaw) {
            const newTargetB64 = btoa(unescape(encodeURIComponent(newTargetRaw)));
            const newTargetWithDiff = highlightDifferences(targetRaw, newTargetRaw);
            newTargetDisplay = `
                <div class="has-revision xlf-revision" data-matecat-id="${matecatId}-xlf">
                    <div class="revision-text" id="text-${matecatId}-xlf">${newTargetWithDiff}<span class="edited-badge" id="badge-${matecatId}-xlf" style="display: none;">EDITED</span></div>
                    <textarea class="revision-textarea" id="textarea-${matecatId}-xlf" data-original-b64="${newTargetB64}">${escapeHtml(newTargetRaw)}</textarea>
                    <div class="button-group">
                        <button class="copy-button" data-text-b64="${newTargetB64}" data-matecat-id="${matecatId}-xlf" onclick="copyToClipboard(this)" title="Copy revision">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                            </svg>
                            Copy
                        </button>
                        <button class="edit-button" data-matecat-id="${matecatId}-xlf" onclick="editRevision(this)" title="Edit revision">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                            Edit
                        </button>
                        <button class="save-button" data-matecat-id="${matecatId}-xlf" onclick="saveRevision(this)" title="Save changes" style="display: none;">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                            Save
                        </button>
                        <button class="cancel-button" data-matecat-id="${matecatId}-xlf" onclick="cancelEdit(this)" title="Cancel editing" style="display: none;">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                            Cancel
                        </button>
                    </div>
                </div>
            `;
        }

        let aiRevisionDisplay = '<em>No AI revision</em>';
        if (aiRevisionRaw) {
            const aiRevisionB64 = btoa(unescape(encodeURIComponent(aiRevisionRaw)));
            const aiRevisionWithDiff = highlightDifferences(targetRaw, aiRevisionRaw);

            let confidenceBadge = '';
            if (confidenceScore) {
                const color = getConfidenceColor(confidenceScore);
                confidenceBadge = `<span class="confidence-badge" style="background-color: ${color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-left: 6px;" title="Confidence Score: ${confidenceScore}%">${confidenceScore}%</span>`;
            }

            aiRevisionDisplay = `
                <div class="has-revision ai-revision" data-matecat-id="${matecatId}-ai">
                    <div class="revision-text" id="text-${matecatId}-ai">${aiRevisionWithDiff}<span class="ai-badge">AI</span>${confidenceBadge}<span class="edited-badge" id="badge-${matecatId}-ai" style="display: none;">EDITED</span></div>
                    <textarea class="revision-textarea" id="textarea-${matecatId}-ai" data-original-b64="${aiRevisionB64}">${escapeHtml(aiRevisionRaw)}</textarea>
                    <div class="button-group">
                        <button class="copy-button" data-text-b64="${aiRevisionB64}" data-matecat-id="${matecatId}-ai" onclick="copyToClipboard(this)" title="Copy AI revision">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                            </svg>
                            Copy
                        </button>
                        <button class="edit-button" data-matecat-id="${matecatId}-ai" onclick="editRevision(this)" title="Edit AI revision">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                            Edit
                        </button>
                        <button class="save-button" data-matecat-id="${matecatId}-ai" onclick="saveRevision(this)" title="Save changes" style="display: none;">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                            Save
                        </button>
                        <button class="cancel-button" data-matecat-id="${matecatId}-ai" onclick="cancelEdit(this)" title="Cancel editing" style="display: none;">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                            Cancel
                        </button>
                    </div>
                </div>
            `;
        }

        tableRowsHtml += `
           <tr class="${rowClass}" data-code="${code}" data-has-revision="${hasRevision}" data-has-ai-revision="${hasAiRevisionAttr}" data-has-xlf-revision="${newTargetRaw ? 'true' : 'false'}" data-state="${state}" data-matecat-id="${matecatId}">
                <td class="id-col">${matecatId}${aiRevisionRaw ? '<span class="ai-badge">✨ AI</span>' : newTargetRaw ? '<span class="xlf-badge">📄 XLF</span>' : ''}</td>
                <td class="state-col">${stateBadge}</td>
                <td class="source-col">${source}</td>
                <td class="target-col" data-raw-target="${escapeHtml(targetRaw)}">${target}</td>
                <td class="new-target-col ${newTargetRaw ? 'has-revision xlf-revision-col' : ''}">${newTargetDisplay}</td>
                <td class="ai-revision-col ${aiRevisionRaw ? 'has-revision ai-revision-col' : ''}">${aiRevisionDisplay}</td>
                <td class="code-col">${codeHtml}</td>
                <td class="comment-col">${commentDisplay}</td>
            </tr>
        `;
    }

    container.innerHTML = `
        ${statsHtml}
        ${filtersHtml}
        <div class="table-wrapper">
            <table id="revisionTable">
                <thead>
                    <tr>
                        <th>ID Matecat</th>
                        <th>State</th>
                        <th>Source</th>
                        <th>Target</th>
                        <th class="xlf-revision-header">📄 Revision</th>
                        <th class="ai-revision-header">✨ AI Revision</th>
                        <th>Code</th>
                        <th>Comment</th>
                    </tr>
                </thead>
                <tbody>
                    ${tableRowsHtml}
                </tbody>
            </table>
        </div>
    `;

    loadSavedEdits();
}

function applyStatFilter(filterType) {
    document.querySelectorAll('.stat-box').forEach(box => {
        box.classList.remove('active');
    });

    if (window.activeStatFilter === filterType && filterType !== 'all') {
        window.activeStatFilter = '';
        filterTable();
        return;
    }

    const codeFilter = document.getElementById('codeFilter');
    const stateFilter = document.getElementById('stateFilter');
    if (codeFilter) codeFilter.value = '';
    if (stateFilter) stateFilter.value = '';

    const activeBox = document.querySelector(`[data-filter="${filterType}"]`);
    if (activeBox) {
        activeBox.classList.add('active');
    }

    if (filterType === 'all') {
    } else     if (filterType === 'error-codes') {
    } else if (filterType === 'major-errors') {
        if (codeFilter) codeFilter.value = 'TE-2';
    }

    window.activeStatFilter = filterType;
    window._statFilterTriggered = true;
    filterTable();
}

function filterTable() {
    const codeFilter = document.getElementById('codeFilter')?.value || '';
    const stateFilter = document.getElementById('stateFilter')?.value || '';
    const idRangeMin = document.getElementById('idRangeMin')?.value;
    const idRangeMax = document.getElementById('idRangeMax')?.value;
    const searchText = (document.getElementById('searchBox')?.value || '').toLowerCase();
    const activeStatFilter = window.activeStatFilter || '';
    const table = document.getElementById('revisionTable');
    if (!table) return;

    if (!window._statFilterTriggered) {
        if (activeStatFilter === 'major-errors' && codeFilter !== 'TE-2') {
            window.activeStatFilter = '';
            document.querySelectorAll('.stat-box').forEach(box => box.classList.remove('active'));
        } else if (activeStatFilter && activeStatFilter !== 'all' && activeStatFilter !== 'major-errors') {
            const codeFilterEl = document.getElementById('codeFilter');
            if (codeFilterEl && codeFilterEl.value) {
                window.activeStatFilter = '';
                document.querySelectorAll('.stat-box').forEach(box => box.classList.remove('active'));
            }
        }
    }
    window._statFilterTriggered = false;

    const rows = table.getElementsByTagName('tr');

    const minId = idRangeMin ? parseInt(idRangeMin) : null;
    const maxId = idRangeMax ? parseInt(idRangeMax) : null;

    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const code = row.getAttribute('data-code') || '';
        const state = row.getAttribute('data-state') || '';
        const hasRevision = row.getAttribute('data-has-revision') === 'true';
        const hasAiRevision = row.getAttribute('data-has-ai-revision') === 'true';
        const source = row.cells[2]?.textContent.toLowerCase() || '';
        const target = row.cells[3]?.textContent.toLowerCase() || '';
        const newTarget = row.cells[4]?.textContent.toLowerCase() || '';
        const aiRevision = row.cells[5]?.textContent.toLowerCase() || '';

        const matecatIdText = row.cells[0]?.textContent || '';
        const matecatIdMatch = matecatIdText.match(/\d+/);
        const matecatId = matecatIdMatch ? parseInt(matecatIdMatch[0]) : null;

        let inRange = true;
        if (minId !== null || maxId !== null) {
            if (matecatId === null) {
                inRange = false;
            } else {
                if (minId !== null && matecatId < minId) inRange = false;
                if (maxId !== null && matecatId > maxId) inRange = false;
            }
        }

        let show = true;
        if (codeFilter && !code.includes(codeFilter)) show = false;
        if (stateFilter && state !== stateFilter) show = false;
        if (!inRange) show = false;
        if (searchText && !source.includes(searchText) && !target.includes(searchText) && !newTarget.includes(searchText) && !aiRevision.includes(searchText)) show = false;

        const hasXlfRevision = row.getAttribute('data-has-xlf-revision') === 'true';
        if (activeStatFilter === 'ai-revisions' && !hasAiRevision) show = false;
        if (activeStatFilter === 'xlf-revisions' && !hasXlfRevision) show = false;
        if (activeStatFilter === 'error-codes' && !code.trim()) show = false;
        if (activeStatFilter === 'major-errors' && !code.includes('TE-2')) show = false;

        row.style.display = show ? '' : 'none';
    }
}

function loadSavedEdits() {
    setTimeout(() => {
        const revisions = document.querySelectorAll('.has-revision[data-matecat-id]');
        revisions.forEach(function (rev) {
            const matecatId = rev.getAttribute('data-matecat-id');
            const savedText = localStorage.getItem('revision_' + matecatId);
            if (savedText) {
                const textDiv = document.getElementById('text-' + matecatId);
                const textarea = document.getElementById('textarea-' + matecatId);
                const badge = document.getElementById('badge-' + matecatId);
                const copyButton = rev.querySelector('.copy-button');

                if (textDiv && textarea && badge && copyButton) {
                    const formattedText = formatTextWithTags(savedText);
                    textDiv.innerHTML = formattedText + '<span class="edited-badge">EDITED</span>';
                    textarea.value = savedText;
                    badge.style.display = 'inline-block';
                    const editedB64 = btoa(unescape(encodeURIComponent(savedText)));
                    copyButton.setAttribute('data-text-b64', editedB64);
                }
            }
        });
    }, 100);
}

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
    loadJobs();

    document.getElementById('uploadArea').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });

    document.getElementById('fileInput').addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
        }
    });

    const uploadArea = document.getElementById('uploadArea');
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });

    document.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            const searchBox = document.getElementById('searchBox');
            if (searchBox) searchBox.focus();
        }
    });
});
