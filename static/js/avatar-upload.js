/**
 * Avatar upload and preview functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const avatarInput = document.getElementById('avatar');
    const avatarPreview = document.getElementById('avatar-preview');
    const avatarContainer = document.getElementById('avatar-preview-container');
    
    if (!avatarInput || !avatarPreview || !avatarContainer) {
        return; // Exit if we're not on a page with avatar functionality
    }
    
    // Function to preview avatar image
    function previewAvatar(file) {
        // Check if the file is an image
        if (!file.type.match('image.*')) {
            alert('Пожалуйста, выберите изображение');
            return;
        }
        
        const reader = new FileReader();
        
        reader.onload = function(e) {
            avatarPreview.src = e.target.result;
        }
        
        reader.readAsDataURL(file);
    }
    
    // Handle file selection via the input
    avatarInput.addEventListener('change', function(e) {
        e.stopPropagation();
        if (this.files && this.files[0]) {
            const file = this.files[0];
            previewAvatar(file);
        }
    });
    
    // Handle click on the avatar container to trigger file selection
    avatarContainer.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        avatarInput.click();
    });
    
    // Prevent defaults for all drag events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        avatarContainer.addEventListener(eventName, function(e) {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });
    
    // Add visual feedback when dragging over
    ['dragenter', 'dragover'].forEach(eventName => {
        avatarContainer.addEventListener(eventName, function() {
            avatarContainer.classList.add('avatar-drag-over');
        }, false);
    });
    
    // Remove visual feedback when drag leaves or on drop
    ['dragleave', 'drop'].forEach(eventName => {
        avatarContainer.addEventListener(eventName, function() {
            avatarContainer.classList.remove('avatar-drag-over');
        }, false);
    });
    
    // Handle the dropped file
    avatarContainer.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files && files.length > 0) {
            // Set the file to the input so it will be submitted with the form
            avatarInput.files = files;
            previewAvatar(files[0]);
        }
    }, false);
    
    // Prevent document level drag and drop to stop browser from opening files
    document.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
    }, false);
    
    document.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
    }, false);
}); 