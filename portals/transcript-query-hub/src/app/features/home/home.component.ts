import { Component, OnInit, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { 
  faMagnifyingGlass, 
  faCloudArrowUp, 
  faFileLines, 
  faBolt,
  faShieldHalved,
  faChartLine,
  faArrowRight,
  faPlay,
  faQuoteLeft
} from '@fortawesome/free-solid-svg-icons';
import { SearchBoxComponent } from '../../shared/components/search-box/search-box.component';

declare var AOS: any;

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, FontAwesomeModule, SearchBoxComponent],
  template: `
    <!-- Hero Section -->
    <section class="relative min-h-[90vh] flex items-center overflow-hidden bg-mesh">
      <!-- Background Elements -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="absolute top-20 left-10 w-72 h-72 bg-tq-primary-400/20 rounded-full blur-3xl animate-float"></div>
        <div class="absolute bottom-20 right-10 w-96 h-96 bg-tq-secondary-400/20 rounded-full blur-3xl animate-float animation-delay-200"></div>
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-tq-accent-400/10 rounded-full blur-3xl"></div>
      </div>

      <div class="container-app relative z-10 py-20">
        <div class="max-w-4xl mx-auto text-center">
          <!-- Badge -->
          <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 backdrop-blur-sm 
                      border border-tq-primary-200 shadow-sm mb-8 animate-fade-in-down"
               data-aos="fade-down">
            <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            <span class="text-sm font-medium text-gray-700">AI-Powered Transcript Analysis</span>
          </div>

          <!-- Headline -->
          <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 leading-tight"
              data-aos="fade-up" data-aos-delay="100">
            Search Your Videos
            <span class="text-gradient block">Like Never Before</span>
          </h1>

          <!-- Subheadline -->
          <p class="text-xl md:text-2xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed"
             data-aos="fade-up" data-aos-delay="200">
            Upload transcripts, ask questions in natural language, and get instant AI-powered answers with source citations.
          </p>

          <!-- Search Box -->
          <div class="max-w-2xl mx-auto mb-8" data-aos="fade-up" data-aos-delay="300">
            <app-search-box
              placeholder="Ask anything about your transcripts..."
              [showSuggestions]="true"
              [suggestions]="sampleQuestions"
              (search)="onSearch($event)">
            </app-search-box>
          </div>

          <!-- Quick Actions -->
          <div class="flex flex-wrap items-center justify-center gap-4" data-aos="fade-up" data-aos-delay="400">
            <a routerLink="/upload" class="btn btn-secondary group">
              <fa-icon [icon]="faCloudArrowUp" class="group-hover:animate-bounce"></fa-icon>
              Upload Transcript
            </a>
            <a routerLink="/transcripts" class="btn btn-ghost group">
              <fa-icon [icon]="faFileLines"></fa-icon>
              Browse Transcripts
              <fa-icon [icon]="faArrowRight" class="text-sm opacity-0 group-hover:opacity-100 transition-opacity"></fa-icon>
            </a>
          </div>

          <!-- Stats -->
          <div class="grid grid-cols-3 gap-8 max-w-lg mx-auto mt-16" data-aos="fade-up" data-aos-delay="500">
            <div class="text-center">
              <p class="text-3xl font-bold text-gradient">10x</p>
              <p class="text-sm text-gray-500">Faster Search</p>
            </div>
            <div class="text-center">
              <p class="text-3xl font-bold text-gradient">99%</p>
              <p class="text-sm text-gray-500">Accuracy</p>
            </div>
            <div class="text-center">
              <p class="text-3xl font-bold text-gradient">24/7</p>
              <p class="text-sm text-gray-500">Available</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Scroll Indicator -->
      <div class="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <div class="w-6 h-10 rounded-full border-2 border-gray-300 flex items-start justify-center p-2">
          <div class="w-1.5 h-3 rounded-full bg-gray-400 animate-pulse"></div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-20 md:py-32 bg-white">
      <div class="container-app">
        <div class="text-center mb-16" data-aos="fade-up">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Powerful Features for <span class="text-gradient">Smart Search</span>
          </h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">
            Everything you need to extract insights from your video transcripts
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          @for (feature of features; track feature.title; let i = $index) {
            <div class="card card-hover p-8 group" 
                 data-aos="fade-up" 
                 [attr.data-aos-delay]="i * 100">
              <div class="w-14 h-14 rounded-2xl flex items-center justify-center mb-6 transition-all duration-300
                          bg-gradient-to-br from-tq-primary-500 to-tq-primary-600 
                          group-hover:scale-110 group-hover:shadow-lg shadow-tq-primary-500/25">
                <fa-icon [icon]="feature.icon" class="text-white text-xl"></fa-icon>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-3">{{ feature.title }}</h3>
              <p class="text-gray-600 leading-relaxed">{{ feature.description }}</p>
            </div>
          }
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="py-20 md:py-32 bg-gray-50">
      <div class="container-app">
        <div class="text-center mb-16" data-aos="fade-up">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            How It <span class="text-gradient">Works</span>
          </h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">
            Get started in three simple steps
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-8 relative">
          <!-- Connection Line (desktop) -->
          <div class="hidden md:block absolute top-16 left-1/4 right-1/4 h-0.5 bg-gradient-to-r from-tq-primary-300 via-tq-secondary-300 to-tq-accent-300"></div>

          @for (step of steps; track step.number; let i = $index) {
            <div class="relative text-center" data-aos="fade-up" [attr.data-aos-delay]="i * 150">
              <!-- Step Number -->
              <div class="w-12 h-12 rounded-full bg-white border-4 border-tq-primary-500 
                          flex items-center justify-center mx-auto mb-6 relative z-10
                          shadow-lg shadow-tq-primary-500/20">
                <span class="text-lg font-bold text-tq-primary-600">{{ step.number }}</span>
              </div>
              
              <h3 class="text-xl font-semibold text-gray-900 mb-3">{{ step.title }}</h3>
              <p class="text-gray-600">{{ step.description }}</p>
            </div>
          }
        </div>

        <!-- CTA -->
        <div class="text-center mt-16" data-aos="fade-up">
          <a routerLink="/upload" class="btn btn-primary btn-lg shadow-xl shadow-tq-primary-500/25 
                                         hover:shadow-tq-glow-lg transition-all duration-300">
            <fa-icon [icon]="faCloudArrowUp"></fa-icon>
            Get Started Now
            <fa-icon [icon]="faArrowRight" class="text-sm"></fa-icon>
          </a>
        </div>
      </div>
    </section>

    <!-- Testimonial / Quote Section -->
    <section class="py-20 md:py-32 bg-gradient-to-br from-tq-primary-600 to-tq-secondary-700 text-white">
      <div class="container-app">
        <div class="max-w-3xl mx-auto text-center" data-aos="fade-up">
          <fa-icon [icon]="faQuoteLeft" class="text-5xl text-white/20 mb-6"></fa-icon>
          <blockquote class="text-2xl md:text-3xl font-light leading-relaxed mb-8">
            "TranscriptQuery has revolutionized how we search through our video content. 
            What used to take hours now takes seconds."
          </blockquote>
          <div class="flex items-center justify-center gap-4">
            <div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
              <span class="text-lg font-bold">JD</span>
            </div>
            <div class="text-left">
              <p class="font-semibold">Jane Doe</p>
              <p class="text-sm text-white/70">Content Manager, TechCorp</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Final CTA -->
    <section class="py-20 md:py-32 bg-white">
      <div class="container-app">
        <div class="max-w-4xl mx-auto text-center" data-aos="fade-up">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Ready to Transform Your <span class="text-gradient">Video Search</span>?
          </h2>
          <p class="text-lg text-gray-600 mb-10 max-w-2xl mx-auto">
            Start uploading your transcripts today and experience the power of AI-driven search.
          </p>
          <div class="flex flex-wrap items-center justify-center gap-4">
            <a routerLink="/upload" class="btn btn-primary btn-lg">
              <fa-icon [icon]="faCloudArrowUp"></fa-icon>
              Upload Your First Transcript
            </a>
            <a routerLink="/search" class="btn btn-secondary btn-lg">
              <fa-icon [icon]="faPlay"></fa-icon>
              Try Demo Search
            </a>
          </div>
        </div>
      </div>
    </section>
  `
})
export class HomeComponent implements OnInit, AfterViewInit {
  // Icons
  faMagnifyingGlass = faMagnifyingGlass;
  faCloudArrowUp = faCloudArrowUp;
  faFileLines = faFileLines;
  faBolt = faBolt;
  faShieldHalved = faShieldHalved;
  faChartLine = faChartLine;
  faArrowRight = faArrowRight;
  faPlay = faPlay;
  faQuoteLeft = faQuoteLeft;

  // Sample questions for suggestions
  sampleQuestions = [
    'What are the main topics discussed?',
    'Summarize the key points',
    'What questions were asked?',
    'Find mentions of pricing'
  ];

  // Features
  features = [
    {
      icon: faMagnifyingGlass,
      title: 'Natural Language Search',
      description: 'Ask questions in plain English and get precise answers from your transcripts instantly.'
    },
    {
      icon: faBolt,
      title: 'Lightning Fast',
      description: 'Get results in milliseconds with our optimized vector search and AI processing.'
    },
    {
      icon: faShieldHalved,
      title: 'Secure & Private',
      description: 'Your data stays yours. All processing is done securely with enterprise-grade encryption.'
    },
    {
      icon: faChartLine,
      title: 'Smart Analytics',
      description: 'Gain insights with sentiment analysis, topic extraction, and trend identification.'
    },
    {
      icon: faFileLines,
      title: 'Multi-Format Support',
      description: 'Upload transcripts in various formats including TXT, SRT, VTT, and JSON.'
    },
    {
      icon: faCloudArrowUp,
      title: 'Easy Upload',
      description: 'Drag and drop your files or paste content directly. We handle the rest.'
    }
  ];

  // Steps
  steps = [
    {
      number: 1,
      title: 'Upload Transcripts',
      description: 'Upload your video transcripts in any supported format.'
    },
    {
      number: 2,
      title: 'AI Processing',
      description: 'Our AI indexes and analyzes your content automatically.'
    },
    {
      number: 3,
      title: 'Search & Discover',
      description: 'Ask questions and get instant, accurate answers.'
    }
  ];

  constructor(private router: Router) {}

  ngOnInit(): void {}

  ngAfterViewInit(): void {
    // Initialize AOS
    if (typeof AOS !== 'undefined') {
      AOS.init({
        duration: 800,
        easing: 'ease-out-cubic',
        once: true,
        offset: 50
      });
    }
  }

  onSearch(query: string): void {
    this.router.navigate(['/search'], { queryParams: { q: query } });
  }
}