document.addEventListener('DOMContentLoaded', function() {
    const insurerSelect = document.getElementById('insurer');
    const policySelect = document.getElementById('policy');
    function updatePolicies(selectedPolicy) {
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
    }
    // On page load, ensure the correct policy is selected
    const selectedPolicy = policySelect.getAttribute('data-selected');
    if (insurerSelect && policySelect) {
        insurerSelect.addEventListener('change', function() {
            updatePolicies();
        });
        // If you want to ensure the correct policy is selected on load (e.g. after POST)
        updatePolicies(selectedPolicy);
    }
});
