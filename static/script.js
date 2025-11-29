// Theme toggle (light / dark) with localStorage
const themeToggle = document.getElementById("themeToggle");
const rootBody = document.body;

const savedTheme = localStorage.getItem("theme-preference");
if (savedTheme === "light") {
  rootBody.classList.add("light");
}

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    rootBody.classList.toggle("light");
    const isLight = rootBody.classList.contains("light");
    localStorage.setItem("theme-preference", isLight ? "light" : "dark");
  });
}

// Mobile nav toggle
const navToggle = document.getElementById("navToggle");
const navLinks = document.querySelector(".nav-links");

if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    navLinks.classList.toggle("open");
  });

  navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      navLinks.classList.remove("open");
    });
  });
}

// Smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    const targetId = this.getAttribute("href");
    if (targetId.length > 1) {
      e.preventDefault();
      const target = document.querySelector(targetId);
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }
  });
});

// Footer year
const yearSpan = document.getElementById("year");
if (yearSpan) {
  yearSpan.textContent = new Date().getFullYear();
}

// Scroll-triggered reveal for sections
const sections = document.querySelectorAll(".anim-section");

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  },
  {
    root: null,
    rootMargin: "0px 0px -20% 0px",
    threshold: 0.15,
  }
);

sections.forEach((section) => observer.observe(section));

// Contact form: send to Flask backend
const contactForm = document.getElementById("contactForm");
const formNote = document.getElementById("formNote");
const sendBtn = document.getElementById("sendBtn");
const btnLabel = sendBtn?.querySelector(".btn-label");

if (contactForm && sendBtn && formNote) {
  contactForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("name")?.value.trim();
    const email = document.getElementById("email")?.value.trim();
    const message = document.getElementById("message")?.value.trim();

    if (!name || !email || !message) {
      formNote.textContent = "Please fill all fields before sending.";
      return;
    }

    try {
      sendBtn.classList.add("loading");
      sendBtn.disabled = true;

      const res = await fetch("/contact", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, email, message }),
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error || "Something went wrong. Try again.");
      }

      formNote.textContent = data.message || "Message sent successfully!";
      formNote.style.color = "#22c55e";

      contactForm.reset();
    } catch (err) {
      console.error(err);
      formNote.textContent = err.message || "Error sending message.";
      formNote.style.color = "#f97373";
    } finally {
      sendBtn.classList.remove("loading");
      sendBtn.disabled = false;
    }
  });
}
