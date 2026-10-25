<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html>
<html b:css='false' xmlns='http://www.w3.org/1999/xhtml' xmlns:b='http://www.google.com/2005/gml/b' xmlns:data='http://www.google.com/2005/gml/data' xmlns:expr='http://www.google.com/2005/gml/expr'>
<head>
    <title><data:blog.pageTitle/></title>
    <meta content='width=device-width, initial-scale=1.0, maximum-scale=5.0' name='viewport'/>
    <meta content='text/html; charset=UTF-8' http-equiv='Content-Type'/>
    
    <!-- SEO Meta Tags -->
    <meta content='VidCaptions - Free AI Audio &amp; Video Caption Generator' name='title'/>
    <meta content='Convert audio, video files, and YouTube links into highly accurate captions and transcripts instantly using OpenAI Whisper AI. 100% Free SaaS tool.' name='description'/>
    <meta content='AI caption generator, free video subtitles, OpenAI Whisper transcriber, YouTube subtitles generator, Urdu captions, Pashto transcription, audio to text' name='keywords'/>
    <meta content='index, follow' name='robots'/>
    
    <!-- OpenGraph Social Tags -->
    <meta expr:content='data:blog.pageTitle' property='og:title'/>
    <meta content='Convert media files and YouTube videos into precise subtitles using OpenAI Whisper AI.' property='og:description'/>
    <meta content='website' property='og:type'/>
    <meta expr:content='data:blog.canonicalUrl' property='og:url'/>

    <b:skin><![CDATA[
        /* Reset & Base Setup */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
            -webkit-text-size-adjust: 100%;
        }

        /* Blogger Outer Wrappers Reset */
        .post-outer, .post, .blog-posts, .main-inner, .column-center-inner {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* ------------------------------------
           1. HIDE BLOG POST TITLE (If required)
           ------------------------------------ */
        .hide-blog-title .post-title,
        .hide-blog-title h2.post-title,
        .hide-blog-title h3.post-title {
            display: none !important;
        }

        /* Header Navigation */
        header {
            background-color: #ffffff;
            border-bottom: 1px solid #e2e8f0;
            padding: 14px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .header-brand a {
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .brand-logo-badge {
            background: #4f46e5;
            color: white;
            font-weight: 800;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 16px;
        }
        .brand-name-text {
            font-size: 20px;
            font-weight: 800;
            color: #0f172a;
        }

        /* Nav & Hamburger Setup */
        nav.nav-menu {
            display: flex;
            gap: 18px;
            align-items: center;
        }
        nav.nav-menu a {
            color: #475569;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            transition: color 0.2s ease;
        }
        nav.nav-menu a:hover {
            color: #4f46e5;
        }

        /* 3-Line Hamburger Icon Button */
        .mobile-toggle-btn {
            display: none;
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #0f172a;
            padding: 4px 8px;
            border-radius: 6px;
            line-height: 1;
        }

        /* Layout Container */
        .page-wrapper {
            max-width: 1200px;
            margin: 25px auto;
            padding: 0 16px;
            display: grid;
            grid-template-columns: 3fr 1fr;
            gap: 25px;
        }

        /* Hero Section */
        .hero-section {
            text-align: center;
            padding: 35px 20px;
            background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            margin-bottom: 25px;
        }
        .hero-section h1 {
            font-size: 28px;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 12px;
            line-height: 1.3;
        }
        .hero-section p {
            font-size: 15px;
            color: #475569;
            max-width: 680px;
            margin: 0 auto 20px auto;
        }
        .cta-button {
            display: inline-block;
            background: #4f46e5;
            color: white !important;
            font-weight: 700;
            font-size: 15px;
            padding: 12px 28px;
            border-radius: 8px;
            text-decoration: none !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
            transition: all 0.2s ease;
        }
        .cta-button:hover {
            background: #4338ca;
            transform: translateY(-2px);
        }

        /* Features Grid */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 18px;
            margin-bottom: 25px;
        }
        .feature-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        .feature-card h3 {
            margin-top: 0;
            font-size: 17px;
            color: #0f172a;
            margin-bottom: 8px;
        }
        .feature-card p, .feature-card ul {
            font-size: 14px;
            color: #475569;
        }
        .feature-card ul {
            padding-left: 18px;
            margin-top: 8px;
        }

        /* SEO Block */
        .seo-content-block {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 25px;
        }
        .seo-content-block h2 {
            font-size: 20px;
            color: #0f172a;
            margin-top: 0;
            margin-bottom: 10px;
        }

        /* Blog Post Display Card */
        .blog-post-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 18px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        }

        /* Sidebar Styling */
        aside {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .widget {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        .widget h2 {
            font-size: 15px;
            color: #0f172a;
            border-bottom: 2px solid #4f46e5;
            padding-bottom: 6px;
            margin-top: 0;
            margin-bottom: 12px;
            text-transform: uppercase;
        }
        .widget ul { list-style: none; padding: 0; }
        .widget li { margin-bottom: 8px; }
        .widget a { color: #475569; text-decoration: none; font-size: 14px; }

        /* Footer */
        footer {
            text-align: center;
            padding: 25px;
            border-top: 1px solid #e2e8f0;
            color: #64748b;
            font-size: 13px;
            margin-top: 50px;
            background: #ffffff;
        }

        /* ------------------------------------
           2. MOBILE RESPONSIVE HAMBURGER MENU
           ------------------------------------ */
        @media (max-width: 900px) {
            .page-wrapper {
                grid-template-columns: 1fr;
                margin: 15px auto;
            }
            .mobile-toggle-btn {
                display: block; /* Show 3-line icon on mobile */
            }
            nav.nav-menu {
                display: none; /* Hide menu links by default on mobile */
                flex-direction: column;
                position: absolute;
                top: 100%;
                left: 0;
                width: 100%;
                background: #ffffff;
                border-bottom: 1px solid #e2e8f0;
                padding: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                gap: 12px;
            }
            nav.nav-menu.active {
                display: flex; /* Toggle menu when clicked */
            }
        }
    ]]></b:skin>
</head>
<body>

    <!-- Header Navigation Section -->
    <header>
        <div class='header-brand'>
            <b:section id='header-logo-section' maxwidgets='1' showaddelement='no'>
                <b:widget id='Header1' locked='true' title='VidCaptions Header' type='Header'>
                    <b:includable id='main'>
                        <a expr:href='data:blog.homepageUrl'>
                            <b:if cond='data:useImage'>
                                <img expr:alt='data:title' expr:src='data:sourceUrl' style='max-height: 40px;'/>
                            <b:else/>
                                <span class='brand-logo-badge'>AI</span>
                                <span class='brand-name-text'><data:title/></span>
                            </b:if>
                        </a>
                    </b:includable>
                    <b:includable id='description'/>
                    <b:includable id='title'/>
                </b:widget>
            </b:section>
        </div>

        <!-- 3-Line Hamburger Icon Button -->
        <button class='mobile-toggle-btn' id='menuToggle' onclick='toggleMobileMenu()'>☰</button>

        <!-- Header Menu Gadget -->
        <b:section class='header-menu' id='header-menu-section' maxwidgets='1' showaddelement='yes'>
            <b:widget id='LinkList1' locked='false' title='Navigation Menu' type='LinkList'>
                <b:widget-settings>
                    <b:widget-setting name='text-0'>Home</b:widget-setting>
                    <b:widget-setting name='link-0'>https://vidcaptions.blogspot.com/</b:widget-setting>
                    <b:widget-setting name='text-1'>Caption Generator</b:widget-setting>
                    <b:widget-setting name='link-1'>https://vidcaptions.blogspot.com/p/caption-generator.html</b:widget-setting>
                    <b:widget-setting name='text-2'>About</b:widget-setting>
                    <b:widget-setting name='link-2'>https://vidcaptions.blogspot.com/#about</b:widget-setting>
                </b:widget-settings>
                <b:includable id='main'>
                    <nav class='nav-menu' id='mobileNav'>
                        <b:loop values='data:links' var='link'>
                            <a expr:href='data:link.target'><data:link.name/></a>
                        </b:loop>
                    </nav>
                </b:includable>
            </b:widget>
        </b:section>
    </header>

    <!-- Main Content Layout -->
    <div class='page-wrapper'>
        <main>
            <!-- Show Homepage Hero Section -->
            <b:if cond='data:view.isHomepage'>
                <div class='hero-section'>
                    <h1>Free AI Audio &amp; Video Caption Generator</h1>
                    <p>Convert audio files and video content into accurate captions using OpenAI Whisper AI.</p>
                    <a class='cta-button' href='/p/caption-generator.html'>🚀 Launch AI Caption Studio</a>
                </div>

                <div class='features-grid'>
                    <div class='feature-card'>
                        <h3>⚡ How to Use</h3>
                        <p>Upload your audio/video file directly and click generate for instant subtitles.</p>
                    </div>
                    <div class='feature-card'>
                        <h3>🌐 Supported Languages</h3>
                        <p>Supports English, Urdu, Pashto, Hindi, Spanish, French, and many more.</p>
                    </div>
                </div>
            </b:if>

            <!-- Blog Posts Display -->
            <b:section id='main-blog-posts' showaddelement='yes'>
                <b:widget id='Blog1' locked='true' title='Blog Posts' type='Blog'>
                    <b:includable id='main'>
                        <div class='blog-posts-container'>
                            <b:loop values='data:posts' var='post'>
                                <article class='blog-post-card'>
                                    <!-- Agar blog title HIDE karna ho to is h2/h3 ko comment out ya remove kar sakte hain -->
                                    <b:if cond='data:post.title'>
                                        <h2 class='post-title' style='font-size: 20px; margin-bottom: 10px;'>
                                            <a expr:href='data:post.url' style='color: #2563eb; text-decoration: none;'><data:post.title/></a>
                                        </h2>
                                    </b:if>
                                    <div class='post-body-snippet'>
                                        <data:post.body/>
                                    </div>
                                </article>
                            </b:loop>
                        </div>
                    </b:includable>
                </b:widget>
            </b:section>
        </main>

        <!-- Right Sidebar -->
        <aside>
            <b:section id='sidebar-section' showaddelement='yes'>
                <b:widget id='Label1' locked='false' title='Categories' type='Label'/>
                <b:widget id='HTML1' locked='false' title='Quick Info' type='HTML'>
                    <b:widget-settings>
                        <b:widget-setting name='content'>Processed securely via OpenAI Whisper cloud models.</b:widget-setting>
                    </b:widget-settings>
                    <b:includable id='main'>
                        <div class='widget'>
                            <h2>🚀 Fast &amp; Secure</h2>
                            <p style='font-size: 13.5px; color: #475569;'><data:content/></p>
                        </div>
                    </b:includable>
                </b:widget>
            </b:section>
        </aside>
    </div>

    <!-- Footer -->
    <footer>
        <p>&#169; 2026 VidCaptions Studio &#8226; Built with OpenAI Whisper &amp; Streamlit</p>
    </footer>

    <!-- JavaScript for Mobile 3-Line Menu Toggle -->
    <script type='text/javascript'>
        function toggleMobileMenu() {
            var nav = document.getElementById('mobileNav');
            if (nav) {
                nav.classList.toggle('active');
            }
        }
    </script>
</body>
</html>
