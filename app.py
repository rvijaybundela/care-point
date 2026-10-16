from flask import Flask, render_template_string, request, jsonify
import sqlite3
import os
import re
import uuid
from datetime import datetime, date
from zoneinfo import ZoneInfo

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, "bookings.db")
IST = ZoneInfo("Asia/Kolkata")
DOCTORS = ("Dr. Arjun Mehta", "Dr. Ananya Rao", "Dr. Vikram Singh")
APPOINTMENT_SLOTS = ("09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
                     "14:00", "14:30", "15:00", "15:30", "16:00", "16:30")

# All HTML, CSS, and JavaScript are kept inside this single app.py file.
HTML = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CarePoint | Compassionate care, closer to you</title>
  <meta name="description" content="CarePoint provides trusted, modern healthcare from a team that puts your wellbeing first.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    :root{--navy:#123c4a;--deep:#0d2e39;--teal:#1c9a9b;--mint:#e7f5f1;--ink:#17313a;--muted:#60747a;--line:#d9e8e5;--white:#fff}
    *{box-sizing:border-box;margin:0}html{scroll-behavior:smooth;scroll-padding-top:80px}body{font-family:"DM Sans",sans-serif;color:var(--ink);background:#fbfdfc;line-height:1.6}a{color:inherit;text-decoration:none}button,input,select,textarea{font:inherit}.wrap{width:min(1160px,90%);margin:auto}
    .topbar{background:var(--deep);color:#d5e6e4;font-size:12px}.topbar .wrap{display:flex;justify-content:space-between;gap:20px;padding:9px 0}.topbar a{color:#fff}
    header{position:sticky;top:0;z-index:10;background:#fffffff2;border-bottom:1px solid var(--line);backdrop-filter:blur(14px)}nav{min-height:76px;display:flex;align-items:center;justify-content:space-between;gap:28px}.brand{display:flex;align-items:center;gap:10px;font:800 22px Manrope;color:var(--navy)}.brand-mark{display:grid;place-items:center;width:35px;height:35px;border-radius:10px;background:var(--teal);color:#fff;font-size:22px}.brand span{color:var(--teal)}.navlinks{display:flex;align-items:center;gap:29px;font-size:14px;font-weight:600;color:#49636a}.navlinks a:hover{color:var(--teal)}.nav-cta,.btn{display:inline-flex;justify-content:center;align-items:center;border:0;border-radius:7px;padding:13px 21px;background:var(--teal);color:#fff;font-weight:700;cursor:pointer;transition:.2s}.nav-cta:hover,.btn:hover{background:#147f81;transform:translateY(-1px)}.menu{display:none;border:0;background:none;color:var(--navy);font-size:25px}
    .hero{overflow:hidden;background:linear-gradient(120deg,#f0faf7 0%,#fff 62%);padding:66px 0 74px}.hero-grid{display:grid;grid-template-columns:1.02fr .98fr;align-items:center;gap:66px}.pill{display:inline-flex;align-items:center;gap:8px;border-radius:99px;background:#d9f1ea;color:#197a75;padding:7px 13px;font-size:12px;font-weight:700;margin-bottom:20px}.pill:before{content:"";width:7px;height:7px;border-radius:50%;background:#34b58a}.hero h1{max-width:610px;font:800 clamp(40px,5vw,67px)/1.08 Manrope;letter-spacing:-2px;color:var(--navy);margin-bottom:22px}.hero h1 em{color:var(--teal);font-style:normal}.hero p{max-width:540px;color:var(--muted);font-size:16px;line-height:1.8;margin-bottom:30px}.hero-actions{display:flex;align-items:center;gap:18px;flex-wrap:wrap}.btn-light{display:inline-flex;align-items:center;gap:8px;color:var(--navy);font-weight:700;padding:12px}.btn-light:hover{color:var(--teal)}.trust{display:flex;align-items:center;gap:12px;margin-top:28px;color:var(--muted);font-size:12px}.avatars{display:flex}.avatars img{width:30px;height:30px;border:2px solid #fff;border-radius:50%;object-fit:cover;margin-left:-7px}.avatars img:first-child{margin-left:0}.hero-photo{position:relative;min-height:540px}.hero-photo:before{content:"";position:absolute;inset:32px -40px 0 45px;background:#d5eee8;border-radius:50% 50% 0 0}.hero-photo img{position:relative;width:100%;height:540px;object-fit:cover;object-position:center top;border-radius:12px;box-shadow:0 22px 55px #123c4a20}.availability{position:absolute;left:-27px;bottom:35px;background:#fff;border-radius:10px;padding:16px 20px;box-shadow:0 14px 35px #123c4a1a;display:flex;align-items:center;gap:12px;font-size:12px;font-weight:700}.availability b{display:block;font-size:19px;color:var(--navy)}.check{display:grid;place-items:center;width:34px;height:34px;border-radius:50%;background:#d9f4e8;color:#1c9a78;font-size:18px}
    .stats{background:var(--navy);color:#fff;padding:25px 0}.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.stat{text-align:center;border-right:1px solid #ffffff25}.stat:last-child{border:0}.stat strong{display:block;font:800 28px Manrope;color:#a9e2d5}.stat span{font-size:12px;color:#c8dcda}
    section{padding:92px 0}.section-head{max-width:620px;margin-bottom:42px}.kicker{display:block;color:var(--teal);font-size:12px;font-weight:800;letter-spacing:1.7px;text-transform:uppercase;margin-bottom:12px}.section-head h2{font:800 clamp(31px,4vw,46px)/1.12 Manrope;color:var(--navy);letter-spacing:-1px;margin-bottom:14px}.section-head p{color:var(--muted);font-size:15px;line-height:1.8}.center{text-align:center;margin-left:auto;margin-right:auto}
    .services{background:#fff}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.card{border:1px solid var(--line);border-radius:10px;padding:28px;background:#fff;transition:.2s}.card:hover{transform:translateY(-5px);box-shadow:0 15px 35px #123c4a12}.icon{width:48px;height:48px;border-radius:12px;display:grid;place-items:center;background:var(--mint);color:var(--teal);font-size:23px;margin-bottom:22px}.card h3{font:700 20px Manrope;color:var(--navy);margin-bottom:10px}.card p{font-size:13px;color:var(--muted);line-height:1.8;margin-bottom:18px}.card a{font-size:13px;font-weight:700;color:var(--teal)}
    .about{background:var(--mint)}.about-grid{display:grid;grid-template-columns:.9fr 1.1fr;gap:70px;align-items:center}.about-photo{height:480px;position:relative}.about-photo img{width:88%;height:100%;object-fit:cover;border-radius:10px}.experience{position:absolute;right:0;bottom:30px;background:var(--navy);color:#fff;border-radius:9px;padding:18px 20px}.experience strong{display:block;font:800 30px Manrope;color:#a9e2d5}.experience span{font-size:12px}.about h2{font:800 clamp(30px,4vw,46px)/1.15 Manrope;color:var(--navy);margin:10px 0 18px;letter-spacing:-1px}.about p{color:var(--muted);font-size:15px;line-height:1.85;margin-bottom:24px}.ticks{display:grid;grid-template-columns:1fr 1fr;gap:14px;list-style:none;margin-bottom:27px}.ticks li{font-size:13px;font-weight:700}.ticks li:before{content:"✓";display:inline-grid;place-items:center;width:20px;height:20px;border-radius:50%;background:#c7eadf;color:#168877;margin-right:8px}
    .team{background:#fff}.team-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.doctor{border:1px solid var(--line);border-radius:10px;overflow:hidden;background:#fff}.doctor img{height:280px;width:100%;object-fit:cover;object-position:center top}.doctor-info{padding:19px}.doctor-info h3{font:700 19px Manrope;color:var(--navy)}.doctor-info p{font-size:13px;color:var(--teal);margin-top:3px}.doctor-info small{display:block;color:var(--muted);font-size:12px;margin-top:10px}
    .features{background:#f7fbfa}.feature-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.feature{background:#fff;border:1px solid var(--line);border-radius:10px;padding:22px}.feature b{display:block;color:var(--navy);font:700 16px Manrope;margin:15px 0 7px}.feature p{font-size:12px;color:var(--muted);line-height:1.75}.feature .icon{margin:0;width:42px;height:42px;font-size:19px}
    .steps{background:#fff}.steps-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:25px}.step{position:relative;padding:5px 24px 8px 56px}.step:not(:last-child):after{content:"";position:absolute;top:22px;right:-8px;width:32px;border-top:1px dashed #9bcac1}.step-number{position:absolute;left:0;top:0;display:grid;place-items:center;width:38px;height:38px;border-radius:50%;background:var(--teal);color:#fff;font-weight:800}.step h3{font:700 18px Manrope;color:var(--navy);margin-bottom:7px}.step p{font-size:13px;color:var(--muted);line-height:1.7}
    .stories{background:var(--mint)}.stories-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:22px}.quote{background:#fff;border-radius:10px;padding:29px;border:1px solid #d3ebe4}.quote-mark{font:800 44px Manrope;line-height:.7;color:#83cbbd}.quote p{font:700 18px/1.6 Manrope;color:var(--navy);margin:18px 0}.quote footer{display:flex;align-items:center;gap:11px;color:var(--muted);font-size:12px}.quote footer strong{display:block;color:var(--navy);font-size:13px}.quote-avatar{width:38px;height:38px;border-radius:50%;object-fit:cover}.faq{background:#fff}.faq-list{max-width:800px;margin:auto}.faq-item{border-bottom:1px solid var(--line)}.faq-question{width:100%;display:flex;justify-content:space-between;align-items:center;padding:20px 0;border:0;background:none;text-align:left;color:var(--navy);font:700 16px Manrope;cursor:pointer}.faq-question span{color:var(--teal);font-size:22px;transition:transform .2s}.faq-answer{display:none;color:var(--muted);font-size:14px;line-height:1.8;padding:0 30px 20px 0}.faq-item.open .faq-answer{display:block}.faq-item.open .faq-question span{transform:rotate(45deg)}
    .appointment{background:var(--navy);color:#fff}.appointment-grid{display:grid;grid-template-columns:.85fr 1.15fr;gap:65px;align-items:center}.appointment h2{font:800 clamp(31px,4vw,46px)/1.15 Manrope;margin:10px 0 18px}.appointment-intro{color:#c8d9d7;line-height:1.8;font-size:15px;margin-bottom:27px}.contact-line{display:flex;gap:12px;align-items:center;margin-top:15px;color:#dbe9e7;font-size:14px}.contact-line b{color:#9bdfd0}.form{background:#fff;border-radius:10px;color:var(--ink);padding:30px}.form h3{font:700 24px Manrope;color:var(--navy);margin-bottom:5px}.form-note{color:var(--muted);font-size:12px;margin-bottom:20px}.row{display:grid;grid-template-columns:1fr 1fr;gap:14px}.group{margin-bottom:15px}.group label{display:block;font-size:12px;font-weight:700;margin-bottom:6px}.group input,.group select,.group textarea{width:100%;border:1px solid #d8e4e2;border-radius:5px;padding:11px 12px;color:var(--ink);outline:none;background:#fff;font-size:13px}.group input:focus,.group select:focus,.group textarea:focus{border-color:var(--teal);box-shadow:0 0 0 3px #1c9a9b18}.group textarea{height:92px;resize:vertical}.form .btn{width:100%;margin-top:3px}.form-message{font-size:13px;margin-top:12px}        .footer{background:#092630;color:#b9ccca;padding:42px 0 28px;font-size:12px}.footer-grid{display:grid;grid-template-columns:1.1fr 1fr .75fr;gap:34px;align-items:start}.footer-brand{color:#fff;font-size:20px}.footer-brand span{color:#78d2c2}.footer-brand .brand-mark{font-size:0}.footer-brand .brand-mark svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}.footer p{margin:15px 0 8px;color:#d7e8e5}.footer small{color:#8eafaa}.footer-map iframe{display:block;width:100%;height:125px;border:0;border-radius:8px;opacity:.9}.footer-map a{display:inline-block;color:#91dfd1;margin-top:8px;font-weight:700}.footer-actions{display:flex;flex-direction:column;gap:10px}.footer-actions strong{color:#fff;font:700 14px Manrope;margin-bottom:4px}.footer-action{display:flex;align-items:center;gap:9px;color:#d7e8e5}.footer-action span{display:grid;place-items:center;width:27px;height:27px;border-radius:7px;background:#1c9a9b;color:#fff}.footer-action svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}.footer-action:hover,.footer-map a:hover{color:#fff}
    @media(max-width:800px){.topbar .wrap{justify-content:center}.topbar .wrap span{display:none}.navlinks{display:none;position:absolute;left:5%;right:5%;top:70px;flex-direction:column;align-items:stretch;gap:0;padding:10px;background:#fff;border:1px solid var(--line);box-shadow:0 12px 25px #123c4a15}.navlinks.open{display:flex}.navlinks a{padding:12px 14px}.nav-cta{margin:5px 14px 12px}.menu{display:block}.hero{padding-top:42px}.hero-grid,.about-grid,.appointment-grid,.stories-grid{grid-template-columns:1fr;gap:40px}.hero-photo{min-height:390px}.hero-photo img{height:390px}.hero-photo:before{inset:20px -12px 0 20px}.availability{left:10px}.stats-grid{grid-template-columns:repeat(2,1fr);gap:20px}.stat:nth-child(2){border:0}.cards,.team-grid{grid-template-columns:1fr 1fr}.feature-grid{grid-template-columns:1fr 1fr}.about-photo{height:390px}.appointment-grid{gap:25px}.step:not(:last-child):after{display:none}.footer-grid{grid-template-columns:1fr 1fr}.footer-grid>div:first-child{grid-column:1/-1}.footer-actions{text-align:left}.footer .wrap{flex-direction:column;text-align:center}}
    @media(max-width:520px){.wrap{width:min(92%,1160px)}section{padding:65px 0}.hero h1{font-size:42px}.hero-photo{min-height:350px}.hero-photo img{height:350px}.cards,.team-grid,.row,.feature-grid,.steps-grid{grid-template-columns:1fr}.ticks{grid-template-columns:1fr}.form{padding:22px}.footer-grid{grid-template-columns:1fr}.footer-grid>div:first-child{grid-column:auto}.footer-map iframe{height:150px}.footer-actions{text-align:center;align-items:center}.footer .wrap{align-items:center}}
  </style>
</head>
<body>
  <div class="topbar"><div class="wrap"><span>Trusted care for every stage of life</span><span>Mon–Sat: 8:00 AM–8:00 PM &nbsp;|&nbsp; <a href="tel:+911234567890">+91 12345 67890</a></span></div></div>
  <header><nav class="wrap"><a class="brand" href="#home"><i class="brand-mark">✚</i>care<span>point</span></a><button class="menu" aria-label="Open menu">☰</button><div class="navlinks"><a href="#home">Home</a><a href="#services">Our services</a><a href="#about">About us</a><a href="#team">Our doctors</a><a href="#faq">FAQs</a><a class="nav-cta" href="#appointment">Book an appointment</a></div></nav></header>
  <main>
    <section class="hero" id="home"><div class="wrap hero-grid"><div><span class="pill">Your health, our priority</span><h1>Better care for a <em>healthier</em> tomorrow.</h1><p>Personalised healthcare, delivered with compassion and backed by modern expertise. We are here to help you and your family feel your best.</p><div class="hero-actions"><a class="btn" href="#appointment">Book an appointment →</a><a class="btn-light" href="#services">Explore our services <span>↗</span></a></div><div class="trust"><div class="avatars"><img src="/static/images/doctor-woman.jpg" alt=""><img src="/static/images/doctor-consultation.jpg" alt=""><img src="/static/images/doctor-hero.jpg" alt=""></div> Trusted by 10,000+ patients</div></div><div class="hero-photo"><img src="/static/images/doctor-hero.jpg" alt="CarePoint doctor in a white coat"><div class="availability"><span class="check">✓</span><div><b>Same-day care</b>Appointments available today</div></div></div></div></section>
    <div class="stats"><div class="wrap stats-grid"><div class="stat"><strong>15+</strong><span>Years of experience</span></div><div class="stat"><strong>25k+</strong><span>Happy patients</span></div><div class="stat"><strong>30+</strong><span>Medical specialists</span></div><div class="stat"><strong>4.9/5</strong><span>Patient rating</span></div></div></div>
    <section class="services" id="services"><div class="wrap"><div class="section-head center"><span class="kicker">How we can help</span><h2>Complete care, all in one place.</h2><p>From everyday check-ups to specialised treatment, our team is here with the right care at every step.</p></div><div class="cards"><article class="card"><div class="icon">♡</div><h3>Primary care</h3><p>Preventive care, health screenings and treatment for your everyday health needs.</p><a href="#appointment">Learn more →</a></article><article class="card"><div class="icon">✚</div><h3>Specialist care</h3><p>Expert consultations from experienced specialists who listen and understand.</p><a href="#appointment">Learn more →</a></article><article class="card"><div class="icon">◉</div><h3>Diagnostics</h3><p>Accurate, convenient testing with clear results and support from our doctors.</p><a href="#appointment">Learn more →</a></article></div></div></section>
    <section class="about" id="about"><div class="wrap about-grid"><div class="about-photo"><img src="/static/images/doctor-consultation.jpg" alt="Doctor ready to care for patients"><div class="experience"><strong>15+</strong><span>years of trusted care</span></div></div><div><span class="kicker">Why CarePoint</span><h2>Care that sees the whole you.</h2><p>Good healthcare is more than treating symptoms. We take time to listen, understand your needs and create a plan that works for your life.</p><ul class="ticks"><li>Experienced medical team</li><li>Patient-first approach</li><li>Modern facilities</li><li>Easy online booking</li></ul><a class="btn" href="#appointment">Meet our team →</a></div></div></section>
    <section class="team" id="team"><div class="wrap"><div class="section-head center"><span class="kicker">Our medical team</span><h2>Experts who care deeply.</h2><p>Meet the people behind our promise of thoughtful, high-quality healthcare.</p></div><div class="team-grid"><article class="doctor"><img src="/static/images/doctor-hero.jpg" alt="Dr. Arjun Mehta"><div class="doctor-info"><h3>Dr. Arjun Mehta</h3><p>General physician</p><small>MBBS, MD · 15 years experience</small></div></article><article class="doctor"><img src="/static/images/doctor-woman.jpg" alt="Dr. Ananya Rao"><div class="doctor-info"><h3>Dr. Ananya Rao</h3><p>Women's health specialist</p><small>MBBS, DGO · 12 years experience</small></div></article><article class="doctor"><img src="/static/images/doctor-consultation.jpg" alt="Dr. Vikram Singh"><div class="doctor-info"><h3>Dr. Vikram Singh</h3><p>Internal medicine</p><small>MBBS, MD · 18 years experience</small></div></article></div></div></section>
    <section class="features"><div class="wrap"><div class="section-head center"><span class="kicker">The CarePoint difference</span><h2>Healthcare designed around you.</h2><p>Small details make a big difference. Every part of your visit is built to feel simple, respectful and reassuring.</p></div><div class="feature-grid"><article class="feature"><div class="icon">◷</div><b>Flexible appointments</b><p>Choose a time that fits your day, including same-day availability.</p></article><article class="feature"><div class="icon">⌁</div><b>Clear communication</b><p>Understand your options with straightforward, judgement-free guidance.</p></article><article class="feature"><div class="icon">♧</div><b>Personal care plans</b><p>Practical next steps shaped around your goals, needs and lifestyle.</p></article><article class="feature"><div class="icon">⌂</div><b>Follow-up support</b><p>We stay connected after your visit so you never feel left on your own.</p></article></div></div></section>
    <section class="steps"><div class="wrap"><div class="section-head center"><span class="kicker">Simple from start to finish</span><h2>Your care journey starts here.</h2></div><div class="steps-grid"><article class="step"><span class="step-number">1</span><h3>Tell us what you need</h3><p>Share a few details through our secure appointment form.</p></article><article class="step"><span class="step-number">2</span><h3>Meet your doctor</h3><p>Have a calm, focused consultation in person or online.</p></article><article class="step"><span class="step-number">3</span><h3>Feel supported</h3><p>Leave with a clear plan and a team ready for your next step.</p></article></div></div></section>
    <section class="stories"><div class="wrap"><div class="section-head center"><span class="kicker">Patient stories</span><h2>Care that makes a difference.</h2></div><div class="stories-grid"><article class="quote"><span class="quote-mark">“</span><p>From booking to consultation, everyone made me feel listened to. I finally left with answers I could understand.</p><footer><img class="quote-avatar" src="/static/images/doctor-woman.jpg" alt=""><span><strong>Priya S.</strong>CarePoint patient</span></footer></article><article class="quote"><span class="quote-mark">“</span><p>The team was kind, organised and never rushed my questions. It is healthcare that genuinely feels human.</p><footer><img class="quote-avatar" src="/static/images/doctor-hero.jpg" alt=""><span><strong>Rahul K.</strong>CarePoint patient</span></footer></article></div></div></section>
    <section class="faq" id="faq"><div class="wrap"><div class="section-head center"><span class="kicker">Helpful answers</span><h2>Questions, answered.</h2><p>Can't find what you need? Contact our team and we will be happy to help.</p></div><div class="faq-list"><div class="faq-item open"><button class="faq-question" type="button">How do I book an appointment?<span>+</span></button><p class="faq-answer">Complete the form below with your preferred date and time. Our team will review your request and contact you to confirm the appointment.</p></div><div class="faq-item"><button class="faq-question" type="button">Can I change or cancel my appointment?<span>+</span></button><p class="faq-answer">Yes. Call us at +91 12345 67890 as soon as possible and our team will help you find another suitable time.</p></div><div class="faq-item"><button class="faq-question" type="button">Do you offer online consultations?<span>+</span></button><p class="faq-answer">Ask about virtual consultation availability when you submit your booking request. We will confirm the available options with you.</p></div></div></div></section>
    <section class="appointment" id="appointment"><div class="wrap appointment-grid"><div><span class="kicker">Let's get you feeling better</span><h2>Ready to take care of your health?</h2><p class="appointment-intro">Book a consultation with one of our caring doctors. Tell us what you need and our team will confirm your appointment shortly.</p><div class="contact-line"><b>☎</b> +91 12345 67890</div><div class="contact-line"><b>✉</b> hello@carepoint.in</div></div><form class="form" id="booking-form"><h3>Book an appointment</h3><p class="form-note">All fields are required. We usually respond within one business day.</p><div class="row"><div class="group"><label for="name">Patient name</label><input id="name" name="name" required maxlength="100"></div><div class="group"><label for="phone">Phone number</label><input id="phone" name="phone" required maxlength="20" inputmode="tel"></div></div><div class="group"><label for="email">Email address</label><input id="email" name="email" type="email" required maxlength="254"></div><div class="group"><label for="doctor">Choose your doctor</label><select id="doctor" name="doctor" required><option value="">Select a doctor</option><option>Dr. Arjun Mehta</option><option>Dr. Ananya Rao</option><option>Dr. Vikram Singh</option></select></div><div class="row"><div class="group"><label for="appointment_date">Preferred date</label><input id="appointment_date" name="appointment_date" type="date" required></div><div class="group"><label for="appointment_time">Available time slot</label><select id="appointment_time" name="appointment_time" required><option value="">Select a time slot</option><option value="09:00">09:00 AM</option><option value="09:30">09:30 AM</option><option value="10:00">10:00 AM</option><option value="10:30">10:30 AM</option><option value="11:00">11:00 AM</option><option value="11:30">11:30 AM</option><option value="14:00">02:00 PM</option><option value="14:30">02:30 PM</option><option value="15:00">03:00 PM</option><option value="15:30">03:30 PM</option><option value="16:00">04:00 PM</option><option value="16:30">04:30 PM</option></select></div></div><button class="btn" type="submit">Request appointment →</button><p class="form-message" id="form-message" role="status"></p></form></div></section>
  </main>
  <footer class="footer"><div class="wrap footer-grid"><div><a class="brand footer-brand" href="#home"><i class="brand-mark" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg></i>care<span>point</span></a><p>Compassionate care, closer to you.</p><small>&copy; 2026 CarePoint. All rights reserved.</small></div><div class="footer-map"><iframe title="CarePoint clinic map" src="https://www.google.com/maps?q=CarePoint+Clinic+New+Delhi&output=embed" loading="lazy"></iframe><a href="https://www.google.com/maps/search/?api=1&query=CarePoint+Clinic+New+Delhi" target="_blank" rel="noopener">Open map directions &rarr;</a></div><div class="footer-actions"><strong>Connect with us</strong><a class="footer-action" href="tel:+911234567890"><span aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.8 19.8 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.12 5.18 2 2 0 0 1 4.11 3h3a2 2 0 0 1 2 1.72c.12.9.33 1.78.62 2.63a2 2 0 0 1-.45 2.11L8 10.73a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.85.29 1.73.5 2.63.62A2 2 0 0 1 22 16.92z"/></svg></span> Call clinic</a><a class="footer-action" href="https://wa.me/911234567890?text=Hello%20CarePoint%2C%20I%20would%20like%20to%20book%20an%20appointment." target="_blank" rel="noopener"><span aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M21 11.5a8.5 8.5 0 0 1-12.5 7.4L3 20l1.1-5.2A8.5 8.5 0 1 1 21 11.5z"/><path d="M8.5 9.5c.3 1.7 1.3 3 3 3.8l1.2-1.1c.2-.2.5-.3.8-.2l1.6-.7c.3-.1.4-.4.3-.7-.2-1-1-1.6-2-1.6-3.6-.2-6.4-3-6.6-6.6 0-1 .6-1.8 1.6-2 .3-.1.6 0 .7.3l.7 1.6c.1.3 0 .6-.2.8z"/></svg></span> WhatsApp</a><a class="footer-action" href="https://www.instagram.com/carepoint.in/" target="_blank" rel="noopener"><span aria-hidden="true"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".75" fill="currentColor" stroke="none"/></svg></span> Instagram</a></div></div></footer>
  <script>
    const menu=document.querySelector(".menu"),links=document.querySelector(".navlinks");menu.addEventListener("click",()=>links.classList.toggle("open"));links.querySelectorAll("a").forEach(a=>a.addEventListener("click",()=>links.classList.remove("open")));
    document.querySelectorAll(".faq-question").forEach(question=>question.addEventListener("click",()=>question.parentElement.classList.toggle("open")));
    const dateInput=document.querySelector("#appointment_date");dateInput.min=new Date().toISOString().split("T")[0];
    document.querySelector("#booking-form").addEventListener("submit",async event=>{event.preventDefault();const form=event.currentTarget,msg=document.querySelector("#form-message"),button=form.querySelector("button");button.disabled=true;button.textContent="Sending…";msg.textContent="";try{const response=await fetch("/book",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(Object.fromEntries(new FormData(form)))});const result=await response.json();if(!response.ok)throw new Error(result.error||"Unable to send request.");msg.style.color="#168877";msg.textContent=result.message;form.reset();dateInput.min=new Date().toISOString().split("T")[0]}catch(error){msg.style.color="#b33a3a";msg.textContent=error.message}finally{button.disabled=false;button.textContent="Request appointment →"}});
  </script>
</body>
</html>

"""

def initialize_database():
    """Create the local booking table the first time the app starts."""
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id TEXT NOT NULL UNIQUE,
                submitted_at TEXT NOT NULL,
                patient_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                doctor TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                UNIQUE (doctor, appointment_date, appointment_time)
            )
            """
        )
        connection.commit()


def save_booking(booking):
    """Save a booking and report a full slot as a conflict."""
    try:
        with sqlite3.connect(DATABASE_FILE) as connection:
            connection.execute(
                """
                INSERT INTO bookings (
                    booking_id, submitted_at, patient_name, phone, email,
                    doctor, appointment_date, appointment_time, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    booking["booking_id"], booking["submitted_at"], booking["name"],
                    booking["phone"], booking["email"], booking["doctor"],
                    booking["date"], booking["time"], "Pending",
                ),
            )
            connection.commit()
    except sqlite3.IntegrityError as exc:
        if "UNIQUE constraint failed: bookings.doctor" in str(exc):
            raise ValueError("This doctor and time slot is already booked. Please choose another slot.") from exc
        raise


def valid_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


@app.get("/")
def home():
    return render_template_string(HTML)


@app.post("/book")
def book():
    data = request.get_json(silent=True) or request.form.to_dict()
    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip()
    doctor = str(data.get("doctor", "")).strip()
    appointment_date = str(data.get("appointment_date", "")).strip()
    appointment_time = str(data.get("appointment_time", "")).strip()

    if not all([name, phone, email, doctor, appointment_date, appointment_time]):
        return jsonify(error="Please complete every required field."), 400
    if len(name) > 100 or len(phone) > 20 or len(email) > 254:
        return jsonify(error="One or more fields are too long."), 400
    if not re.fullmatch(r"[0-9+() -]{8,20}", phone):
        return jsonify(error="Please enter a valid phone number."), 400
    if not valid_email(email):
        return jsonify(error="Please enter a valid email address."), 400
    if doctor not in DOCTORS:
        return jsonify(error="Please select a valid doctor."), 400

    try:
        selected_date = date.fromisoformat(appointment_date)
        selected_time = datetime.strptime(appointment_time, "%H:%M").time()
    except ValueError:
        return jsonify(error="Please select a valid appointment date and time."), 400
    if appointment_time not in APPOINTMENT_SLOTS:
        return jsonify(error="Please select an available time slot."), 400

    now_ist = datetime.now(IST)
    if selected_date < now_ist.date():
        return jsonify(error="Please select today or a future date."), 400
    if selected_date == now_ist.date() and selected_time <= now_ist.time().replace(tzinfo=None):
        return jsonify(error="Please select a future time."), 400

    booking_id = "BK-" + uuid.uuid4().hex[:10].upper()
    submitted_at = now_ist.strftime("%Y-%m-%d %H:%M:%S")

    booking = {
        "booking_id": booking_id,
        "submitted_at": submitted_at,
        "name": name,
        "phone": phone,
        "email": email,
        "doctor": doctor,
        "date": selected_date.isoformat(),
        "time": selected_time.strftime("%H:%M"),
    }
    try:
        save_booking(booking)
    except ValueError as exc:
        return jsonify(error=str(exc)), 409
    except sqlite3.Error:
        app.logger.exception("Local booking database save failed")
        return jsonify(
            error="We couldn't save your booking request. Please try again later or contact us directly."
        ), 500

    return jsonify(
        message=f"Booking request received! Your reference is {booking_id}. We will contact you to confirm the appointment.",
        booking_id=booking_id
    ), 201


@app.get("/health")
def health():
    database_ready = os.path.isfile(DATABASE_FILE)
    return jsonify(status="ok", local_database=database_ready)


initialize_database()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
