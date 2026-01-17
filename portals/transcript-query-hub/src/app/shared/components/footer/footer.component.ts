import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { 
  faGithub, 
  faTwitter, 
  faLinkedin 
} from '@fortawesome/free-brands-svg-icons';
import { 
  faHeart,
  faEnvelope
} from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [CommonModule, RouterModule, FontAwesomeModule],
  template: `
    <footer class="bg-gray-900 text-gray-300">
      <!-- Main Footer -->
      <div class="container-app py-12 md:py-16">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
          <!-- Brand -->
          <div class="lg:col-span-1">
            <a routerLink="/" class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-tq-primary-500 to-tq-secondary-500 
                          flex items-center justify-center">
                <span class="text-white font-bold text-lg">TQ</span>
              </div>
              <div>
                <h3 class="text-lg font-bold text-white">TranscriptQuery</h3>
                <p class="text-xs text-gray-400">Hub</p>
              </div>
            </a>
            <p class="text-sm text-gray-400 mb-4 max-w-xs">
              AI-powered transcript search and insights. Get instant answers from your video content.
            </p>
            <div class="flex items-center gap-3">
              <a href="#" class="social-link" aria-label="GitHub">
                <fa-icon [icon]="faGithub"></fa-icon>
              </a>
              <a href="#" class="social-link" aria-label="Twitter">
                <fa-icon [icon]="faTwitter"></fa-icon>
              </a>
              <a href="#" class="social-link" aria-label="LinkedIn">
                <fa-icon [icon]="faLinkedin"></fa-icon>
              </a>
              <a href="mailto:support&#64;transcriptquery.com" class="social-link" aria-label="Email">
                <fa-icon [icon]="faEnvelope"></fa-icon>
              </a>
            </div>
          </div>

          <!-- Quick Links -->
          <div>
            <h4 class="text-white font-semibold mb-4">Quick Links</h4>
            <ul class="space-y-2">
              <li><a routerLink="/" class="footer-link">Home</a></li>
              <li><a routerLink="/search" class="footer-link">Search</a></li>
              <li><a routerLink="/transcripts" class="footer-link">Transcripts</a></li>
              <li><a routerLink="/upload" class="footer-link">Upload</a></li>
            </ul>
          </div>

          <!-- Resources -->
          <div>
            <h4 class="text-white font-semibold mb-4">Resources</h4>
            <ul class="space-y-2">
              <li><a href="#" class="footer-link">Documentation</a></li>
              <li><a href="#" class="footer-link">API Reference</a></li>
              <li><a href="#" class="footer-link">Tutorials</a></li>
              <li><a href="#" class="footer-link">FAQ</a></li>
            </ul>
          </div>

          <!-- Support -->
          <div>
            <h4 class="text-white font-semibold mb-4">Support</h4>
            <ul class="space-y-2">
              <li><a href="#" class="footer-link">Help Center</a></li>
              <li><a href="#" class="footer-link">Contact Us</a></li>
              <li><a href="#" class="footer-link">Privacy Policy</a></li>
              <li><a href="#" class="footer-link">Terms of Service</a></li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="border-t border-gray-800">
        <div class="container-app py-6">
          <div class="flex flex-col md:flex-row items-center justify-between gap-4">
            <p class="text-sm text-gray-400">
              © {{ currentYear }} TranscriptQuery. All rights reserved.
            </p>
            <p class="text-sm text-gray-400 flex items-center gap-1">
              Made with <fa-icon [icon]="faHeart" class="text-red-500 text-xs"></fa-icon> 
              using Angular & AI
            </p>
          </div>
        </div>
      </div>
    </footer>
  `,
  styles: [`
    .social-link {
      @apply w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center
             text-gray-400 transition-all duration-300
             hover:bg-tq-primary-600 hover:text-white hover:scale-110;
    }
    
    .footer-link {
      @apply text-sm text-gray-400 transition-colors duration-200
             hover:text-tq-primary-400 hover:underline;
    }
  `]
})
export class FooterComponent {
  faGithub = faGithub;
  faTwitter = faTwitter;
  faLinkedin = faLinkedin;
  faHeart = faHeart;
  faEnvelope = faEnvelope;

  currentYear = new Date().getFullYear();
}