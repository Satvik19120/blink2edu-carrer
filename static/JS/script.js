// Toggle between Login and Register forms
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');

loginBtn.addEventListener('click', () => {
  loginBtn.classList.add('active');
  registerBtn.classList.remove('active');
  loginForm.classList.add('active');
  registerForm.classList.remove('active');
});

registerBtn.addEventListener('click', () => {
  registerBtn.classList.add('active');
  loginBtn.classList.remove('active');
  registerForm.classList.add('active');
  loginForm.classList.remove('active');
});

// Show/Hide Password
function togglePassword(inputId, iconId) {
  const input = document.getElementById(inputId);
  const icon = document.getElementById(iconId);
  icon.addEventListener('click', () => {
    if (input.type === 'password') {
      input.type = 'text';
      icon.classList.replace('bx-show', 'bx-hide');
    } else {
      input.type = 'password';
      icon.classList.replace('bx-hide', 'bx-show');
    }
  });
}
togglePassword('loginPassword', 'toggleLoginPassword');
togglePassword('registerPassword', 'toggleRegisterPassword');



// script for create_assignment page
// Delete Confirmation Modal
document.querySelectorAll('.delete-form').forEach(form => {
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const modal = document.getElementById('deleteModal');
        const deleteBtn = document.getElementById('modalDelete');

        modal.style.display = 'flex';

        // Only allow one submit per modal open
        const confirmDelete = () => {
            form.submit();
            modal.style.display = 'none';
            deleteBtn.removeEventListener('click', confirmDelete);
        };

        deleteBtn.addEventListener('click', confirmDelete);

        document.getElementById('modalCancel').onclick = () => {
            modal.style.display = 'none';
            deleteBtn.removeEventListener('click', confirmDelete);
        };
    });
});
