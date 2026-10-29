(function () {
  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  function showError(box, message) {
    box.textContent = message;
    box.classList.remove('d-none');
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.toast-container .toast').forEach(function (toastEl) {
      bootstrap.Toast.getOrCreateInstance(toastEl).show();
    });

    const modalEl = document.getElementById('crudModal');
    if (modalEl) {
      const form = document.getElementById('crudForm');
      const errorBox = document.getElementById('crudFormError');
      const titleEl = document.getElementById('crudModalTitle');
      const submitBtn = document.getElementById('crudSubmitBtn');
      const idInput = form.querySelector('input[name="id"]');

      modalEl.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const mode = button && button.dataset.mode === 'edit' ? 'edit' : 'create';

        form.reset();
        errorBox.textContent = '';
        errorBox.classList.add('d-none');
        idInput.value = mode === 'edit' && button ? button.dataset.id : '';
        titleEl.textContent = mode === 'edit' ? modalEl.dataset.editTitle : modalEl.dataset.createTitle;
        submitBtn.textContent = mode === 'edit' ? 'Save Changes' : 'Save';

        form.querySelectorAll('[data-required-create]').forEach(function (el) {
          el.required = mode === 'create';
        });

        if (mode === 'edit' && button) {
          Array.prototype.forEach.call(form.elements, function (el) {
            if (!el.name || el.name === 'id' || el.name === 'csrfmiddlewaretoken') return;
            const attr = 'data-' + el.name.replace(/_/g, '-');
            if (button.hasAttribute(attr)) el.value = button.getAttribute(attr);
          });
        }
      });

      form.addEventListener('submit', function (event) {
        event.preventDefault();
        errorBox.classList.add('d-none');
        submitBtn.disabled = true;

        fetch(form.dataset.url, {
          method: 'POST',
          headers: { 'X-CSRFToken': getCookie('csrftoken') },
          body: new FormData(form),
        })
          .then(function (response) {
            return response.json().catch(function () { return {}; }).then(function (data) {
              if (!response.ok) throw new Error(data.error || 'Something went wrong.');
              return data;
            });
          })
          .then(function () {
            window.location.reload();
          })
          .catch(function (error) {
            showError(errorBox, error.message);
          })
          .finally(function () {
            submitBtn.disabled = false;
          });
      });
    }

    const deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
      const deleteBtn = document.getElementById('deleteConfirmBtn');
      let deleteUrl = '';

      deleteModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        deleteUrl = button ? button.dataset.deleteUrl : '';
        document.getElementById('deleteLabel').textContent = button ? button.dataset.label : '';
      });

      deleteBtn.addEventListener('click', function () {
        if (!deleteUrl) return;
        deleteBtn.disabled = true;

        fetch(deleteUrl, {
          method: 'POST',
          headers: { 'X-CSRFToken': getCookie('csrftoken') },
        })
          .then(function (response) {
            return response.json().catch(function () { return {}; }).then(function (data) {
              if (!response.ok) throw new Error(data.error || 'Could not delete.');
              return data;
            });
          })
          .then(function () {
            window.location.reload();
          })
          .catch(function (error) {
            alert(error.message);
          })
          .finally(function () {
            deleteBtn.disabled = false;
          });
      });
    }
  });
})();
