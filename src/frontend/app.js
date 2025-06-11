const imageUpload = document.getElementById('image-upload');
const imagePreview = document.getElementById('image-preview');
const imagePreviewImage = imagePreview.querySelector('.image-preview__image');
const imagePreviewDefaultText = imagePreview.querySelector('.image-preview__default-text');
const analyzeButton = document.getElementById('analyze-button');
const resultsSection = document.getElementById('results-section');
const loader = document.getElementById('loader');
const resultsContent = document.getElementById('results-content');

const API_ENDPOINT = 'http://localhost:8000/api/analyze';

let uploadedFile = null;

imageUpload.addEventListener('change', (event) => {
    const file = event.target.files[0];

    if (file) {
        uploadedFile = file;
        const reader = new FileReader();

        imagePreviewDefaultText.style.display = 'none';
        imagePreviewImage.style.display = 'block';

        reader.addEventListener('load', () => {
            imagePreviewImage.setAttribute('src', reader.result);
        });

        reader.readAsDataURL(file);
        analyzeButton.disabled = false;
    } else {
        uploadedFile = null;
        imagePreviewDefaultText.style.display = 'block';
        imagePreviewImage.style.display = 'none';
        imagePreviewImage.setAttribute('src', '');
        analyzeButton.disabled = true;
    }
});

analyzeButton.addEventListener('click', async () => {
    if (!uploadedFile) {
        alert('Please upload an image first.');
        return;
    }

    loader.style.display = 'block';
    resultsContent.innerHTML = '';
    resultsSection.scrollIntoView({ behavior: 'smooth' });

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        displayResults(data);

    } catch (error) {
        console.error('Error analyzing image:', error);
        resultsContent.innerHTML = `<p style="color: red;">An error occurred during analysis. Please check the console and ensure the backend is running.</p>`;
    } finally {
        loader.style.display = 'none';
    }
});

function displayResults(data) {
    const { analysis, fashionTips, suggestedItems } = data;
    
    let html = `
        <div class="analysis-details">
            <h3>Outfit Analysis</h3>
            <p><strong>Description:</strong> ${analysis.description}</p>
            <p><strong>Color Tones:</strong> ${analysis.colorTones}</p>
            <p><strong>Core Apparel:</strong> ${analysis.coreApparel}</p>
            <p><strong>Accessories:</strong> ${analysis.accessories}</p>
        </div>

        <div class="fashion-tips">
            <h3>Fashion Tips</h3>
            <p>${fashionTips}</p>
        </div>

        <div class="suggested-items">
            <h3>Suggested Items from Nordstrom</h3>
            <div class="suggested-items-grid">
    `;

    suggestedItems.forEach(item => {
        html += `
            <div class="item-card">
                <img src="${item.imageUrl}" alt="${item.name}">
                <div class="item-card-content">
                    <h4>${item.name}</h4>
                    <p>${item.description}</p>
                    <a href="${item.productUrl}" target="_blank">View Product</a>
                </div>
            </div>
        `;
    });

    html += `
            </div>
        </div>
    `;

    resultsContent.innerHTML = html;
} 