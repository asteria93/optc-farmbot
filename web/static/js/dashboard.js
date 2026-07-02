/**
 * Dashboard JavaScript
 * Handles dashboard updates and statistics
 */

async function updateStats() {
    try {
        const accountStats = await api.call('/stats/accounts');
        const farmingStats = await api.call('/stats/farming');
        
        document.getElementById('total-accounts').textContent = accountStats.total_accounts;
        document.getElementById('active-sessions').textContent = farmingStats.active_sessions;
        document.getElementById('total-runs').textContent = farmingStats.total_runs;
        document.getElementById('total-rewards').textContent = accountStats.total_rewards_earned.toLocaleString();
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

async function loadActivityLog() {
    try {
        const response = await api.call('/farming/sessions');
        const activityDiv = document.getElementById('activity-log');
        
        if (response.sessions.length === 0) {
            activityDiv.innerHTML = '<p>No farming activity yet</p>';
            return;
        }
        
        const html = response.sessions.map(session => `
            <div class="activity-item">
                <strong>Account:</strong> ${session.account_id}<br>
                <strong>Mode:</strong> ${session.farming_mode}<br>
                <strong>Status:</strong> <span style="color: ${session.status === 'active' ? 'green' : 'gray'}">${session.status}</span><br>
                <strong>Started:</strong> ${api.formatDate(session.start_time)}<br>
                <strong>Runs:</strong> ${session.total_runs}
            </div>
        `).join('');
        
        activityDiv.innerHTML = html;
    } catch (error) {
        console.error('Error loading activity log:', error);
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    updateStats();
    loadActivityLog();
    
    // Refresh stats every 10 seconds
    setInterval(updateStats, 10000);
    setInterval(loadActivityLog, 15000);
});
