/**
 * Portfolio JavaScript
 * Handles contact form submission to Python Flask backend,
 * navigation toggle, back to top scrolling, and dynamic footer year.
 */

document.addEventListener("DOMContentLoaded", () => {
  // --- Contact Form Handling via Python Flask Backend ---
  const contactForm = document.getElementById("contactForm");
  const submitBtn = document.getElementById("submitBtn");
  const formStatus = document.getElementById("formStatus");

  if (contactForm && formStatus && submitBtn) {
    contactForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      if (!contactForm.reportValidity()) {
        return;
      }

      const nameInput = document.getElementById("name");
      const emailInput = document.getElementById("email");
      const messageInput = document.getElementById("message");

      const name = nameInput.value.trim();
      const email = emailInput.value.trim();
      const message = messageInput.value.trim();

      if (!name || !email || !message) {
        formStatus.textContent = "Please fill in all fields.";
        formStatus.style.color = "#f87171";
        return;
      }

      // Disable button and indicate sending
      submitBtn.disabled = true;
      const originalBtnText = submitBtn.innerHTML;
      submitBtn.textContent = "Sending...";
      formStatus.textContent = "Sending your message...";
      formStatus.style.color = "var(--accent)";

      try {
        const response = await fetch("/send-message", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ name, email, message })
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {
          formStatus.textContent = data.message || "Message sent successfully! Thank you for contacting me.";
          formStatus.style.color = "#4ade80"; // Success green
          contactForm.reset();
        } else {
          formStatus.textContent = data.error || "Unable to send your message. Please try again later.";
          formStatus.style.color = "#f87171"; // Error red
        }
      } catch (error) {
        console.error("Error sending message:", error);
        formStatus.textContent = "Network error. Please check your connection and try again.";
        formStatus.style.color = "#f87171";
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      }
    });
  }

  // --- Mobile Navigation Toggle ---
  const menuToggle = document.getElementById("menuToggle");
  const navMenu = document.getElementById("navMenu");

  if (menuToggle && navMenu) {
    menuToggle.addEventListener("click", () => {
      const isOpen = navMenu.classList.toggle("open");
      menuToggle.setAttribute("aria-expanded", isOpen);
      menuToggle.textContent = isOpen ? "✕" : "☰";
    });

    // Close menu when navigation link is clicked
    navMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        if (navMenu.classList.contains("open")) {
          navMenu.classList.remove("open");
          menuToggle.setAttribute("aria-expanded", "false");
          menuToggle.textContent = "☰";
        }
      });
    });
  }

  // --- Back to Top Button ---
  const backToTop = document.getElementById("backToTop");
  if (backToTop) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 300) {
        backToTop.classList.add("visible");
      } else {
        backToTop.classList.remove("visible");
      }
    });

    backToTop.addEventListener("click", () => {
      window.scrollTo({
        top: 0,
        behavior: "smooth"
      });
    });
  }

  // --- Dynamic Footer Copyright Year ---
  const yearSpan = document.getElementById("year");
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
  }
});
