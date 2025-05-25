document.addEventListener('DOMContentLoaded', function() {
    const insurerSelect = document.getElementById('insurer');
    const policySelect = document.getElementById('policy');
    const selectedPolicy = policySelect.getAttribute('data-selected');
    insurerSelect.addEventListener('change', function() {
        fetch(`/api/policies/${insurerSelect.value}`)
            .then(res => res.json())
            .then(policies => {
                policySelect.innerHTML = '';
                policies.forEach(function(policy) {
                    const opt = document.createElement('option');
                    opt.value = policy.id;
                    opt.textContent = policy.name;
                    if (String(policy.id) === String(selectedPolicy)) {
                        opt.selected = true;
                    }
                    policySelect.appendChild(opt);
                });
            });
    });
});
