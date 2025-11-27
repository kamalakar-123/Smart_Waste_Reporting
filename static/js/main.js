// main.js - handles geolocation and UI helpers
// Initialize AOS (in case base doesn't call it)
if (typeof AOS !== 'undefined') {
  AOS.init({ duration: 700 });
}

// Geolocation logic: called on complaint form
document.addEventListener('DOMContentLoaded', function () {
  var getLocBtn = document.getElementById('getLocationBtn');
  if (getLocBtn) {
    getLocBtn.addEventListener('click', function () {
      var display = document.getElementById('coordsDisplay');
      if (!navigator.geolocation) {
        display.textContent = 'Geolocation not supported by your browser.';
        return;
      }
      display.textContent = 'Locating...';
      navigator.geolocation.getCurrentPosition(function (position) {
        var lat = position.coords.latitude.toFixed(6);
        var lng = position.coords.longitude.toFixed(6);
        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lng;
        display.textContent = 'Coordinates: ' + lat + ', ' + lng;
      }, function (err) {
        display.textContent = 'Unable to retrieve location: ' + err.message;
      }, { enableHighAccuracy: true, timeout: 10000 });
    });
  }
  // Auto-dismiss flash notifications after 2 seconds
  var flashes = document.querySelectorAll('.flash');
  if (flashes && flashes.length) {
    flashes.forEach(function (el) {
      // Wait 2000ms, then fade and remove
      setTimeout(function () {
        el.classList.add('hide');
        // Remove from DOM after CSS transition (500ms)
        setTimeout(function () { try { el.remove(); } catch (e) {} }, 500);
      }, 2000);
    });
  }
  
  // Password show/hide toggles
  var toggles = document.querySelectorAll('.pw-toggle');
  toggles.forEach(function (t) {
    t.addEventListener('click', function () {
      // find previous sibling input with class pw-input
      var parent = t.closest('.pw-group');
      if (!parent) return;
      var input = parent.querySelector('.pw-input');
      if (!input) return;
      if (input.type === 'password') {
        input.type = 'text';
        t.classList.remove('bx-hide');
        t.classList.add('bx-show');
      } else {
        input.type = 'password';
        t.classList.remove('bx-show');
        t.classList.add('bx-hide');
      }
    });
  });

  // Client-side register confirm password validation
  var regForm = document.querySelector('form[action="' + (window.location.pathname === '/register' ? '/register' : '') + '"]');
  // Simpler approach: select register form by checking if it has an input named confirm_password
  var registerForm = document.querySelector('form input[name="confirm_password"]');
  if (registerForm) {
    var form = registerForm.closest('form');
    form.addEventListener('submit', function (e) {
      var pw = form.querySelector('input[name="password"]').value;
      var conf = form.querySelector('input[name="confirm_password"]').value;
      if (pw !== conf) {
        e.preventDefault();
        alert('Passwords do not match. Please confirm the same password.');
        return false;
      }
    });
  }

  // Image preview for camera/file inputs
  function previewFile(inputEl, previewImgId) {
    var file = inputEl.files && inputEl.files[0];
    var img = document.getElementById(previewImgId);
    if (!img) return;
    if (!file) {
      img.style.display = 'none';
      img.src = '';
      return;
    }
    var reader = new FileReader();
    reader.onload = function (e) {
      img.src = e.target.result;
      img.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }

  var beforeInput = document.getElementById('image_before');
  if (beforeInput) {
    beforeInput.addEventListener('change', function () { previewFile(beforeInput, 'beforePreview'); });
  }
  // Explicit camera/file buttons
  var useCameraBtn = document.getElementById('useCameraBtn');
  var chooseFileBtn = document.getElementById('chooseFileBtn');
  // Make 'Use Camera' more reliable across devices by creating a fresh input
  if (useCameraBtn) {
    useCameraBtn.addEventListener('click', function () {
      var form = (beforeInput && beforeInput.closest) ? beforeInput.closest('form') : document.querySelector('form');
      if (!form) return;
      // Remove any existing hidden input so we can create a fresh one
      if (beforeInput && beforeInput.parentNode === form) {
        try { form.removeChild(beforeInput); } catch (e) {}
      }
      var newInput = document.createElement('input');
      newInput.type = 'file';
      newInput.name = 'image_before';
      newInput.id = 'image_before';
      newInput.accept = 'image/*';
      newInput.setAttribute('capture', 'environment');
      newInput.style.display = 'none';
      form.appendChild(newInput);
      beforeInput = newInput;
      newInput.addEventListener('change', function () { previewFile(newInput, 'beforePreview'); });
      // click to open camera / picker (mobile should open camera)
      newInput.click();
    });
  }
  if (chooseFileBtn) {
    chooseFileBtn.addEventListener('click', function () {
      var form = (beforeInput && beforeInput.closest) ? beforeInput.closest('form') : document.querySelector('form');
      if (!form) return;
      // If there's already an input in the DOM, remove capture and click it.
      if (beforeInput && beforeInput.parentNode === form) {
        try { beforeInput.removeAttribute('capture'); } catch (e) {}
        beforeInput.click();
        return;
      }
      // Otherwise create a fresh file input without capture
      var newInput = document.createElement('input');
      newInput.type = 'file';
      newInput.name = 'image_before';
      newInput.id = 'image_before';
      newInput.accept = 'image/*';
      newInput.style.display = 'none';
      form.appendChild(newInput);
      beforeInput = newInput;
      newInput.addEventListener('change', function () { previewFile(newInput, 'beforePreview'); });
      newInput.click();
    });
  }
  var afterInput = document.getElementById('image_after');
  if (afterInput) {
    afterInput.addEventListener('change', function () { previewFile(afterInput, 'afterPreview'); });
  }

  // Tap-to-open behavior: clicking the photo card should open file picker/camera
  var beforeCard = document.querySelector('.photo-card[data-target="before"]');
  if (beforeCard && beforeInput) {
    beforeCard.addEventListener('click', function (e) {
      // avoid triggering when clicking within controls like buttons
      if (e.target.tagName.toLowerCase() === 'button' || e.target.tagName.toLowerCase() === 'a') return;
      beforeInput.click();
    });
    // also allow keyboard activation
    beforeCard.setAttribute('tabindex', '0');
    beforeCard.addEventListener('keypress', function (e) { if (e.key === 'Enter' || e.key === ' ') beforeInput.click(); });
  }
  var afterCard = document.querySelector('.photo-card[data-target="after"]');
  if (afterCard && afterInput) {
    afterCard.addEventListener('click', function (e) {
      if (e.target.tagName.toLowerCase() === 'button' || e.target.tagName.toLowerCase() === 'a') return;
      afterInput.click();
    });
    afterCard.setAttribute('tabindex', '0');
    afterCard.addEventListener('keypress', function (e) { if (e.key === 'Enter' || e.key === ' ') afterInput.click(); });
  }
});

// Small helper: truncate text in JS if needed (not required server-side)
function truncateText(text, n) {
  return text.length > n ? text.substr(0, n-1) + '…' : text;
}
