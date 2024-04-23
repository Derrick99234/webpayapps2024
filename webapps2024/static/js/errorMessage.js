document.addEventListener("DOMContentLoaded", function () {
  const notificationContainer = document.createElement("div");
  notificationContainer.classList.add("notification-container");
  document.body.appendChild(notificationContainer);

  for (const message of messages) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("notification");
    messageDiv.textContent = message;
    notificationContainer.appendChild(messageDiv);
  }

  // Function to remove notifications after 5 seconds
  setTimeout(function () {
    const notifications = document.querySelectorAll(".notification");
    notifications.forEach(function (notification) {
      notification.remove();
    });
  }, 5000);
});
