import { Component, OnInit, HostListener, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { 
  faMagnifyingGlass, 
  faCloudArrowUp, 
  faFileLines,
  faBars,
  faXmark,
  faCircleQuestion,
  faGear,
  faHome
} from '@fortawesome/free-solid-svg-icons';

interface NavItem {
  label: string;
  route: string;
  icon: any;
  exact?: boolean;
}

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule, FontAwesomeModule],
  template: `
    <header class="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
            [ngClass]="{
              'bg-white/95 backdrop-blur-md shadow-md': isScrolled(),
              'bg-transparent': !isScrolled()
            }">
      <nav class="container-app">
        <div class="flex items-center justify-between h-16 md:h-20">
          <!-- Logo -->
          <a routerLink="/" class="flex items-center gap-3 group">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-tq-primary-600 to-tq-secondary-600 
                        flex items-center justify-center shadow-lg shadow-tq-primary-500/25
                        group-hover:shadow-tq-glow transition-all duration-300
                        group-hover:scale-105">
              <span class="text-white font-bold text-lg">TQ</span>
            </div>
            <div class="hidden sm:block">
              <h1 class="text-lg font-bold text-gray-900 group-hover:text-tq-primary-600 transition-colors">
                TranscriptQuery
              </h1>
              <p class="text-xs text-gray-500 -mt-1">Hub</p>
            </div>
          </a>

          <!-- Desktop Navigation -->
          <div class="hidden md:flex items-center gap-1">
            @for (item of navItems; track item.route) {
              <a [routerLink]="item.route" 
                 routerLinkActive="nav-link-active"
                 [routerLinkActiveOptions]="{exact: item.exact ?? false}"
                 class="nav-link group">
                <fa-icon [icon]="item.icon" class="text-sm opacity-70 group-hover:opacity-100"></fa-icon>
                {{ item.label }}
              </a>
            }
          </div>

          <!-- Desktop Actions -->
          <div class="hidden md:flex items-center gap-3">
            <button class="p-2 rounded-full hover:bg-gray-100 transition-colors" 
                    title="Help & Support">
              <fa-icon [icon]="faCircleQuestion" class="text-gray-500 hover:text-tq-primary-600"></fa-icon>
            </button>
            <button class="p-2 rounded-full hover:bg-gray-100 transition-colors"
                    title="Settings">
              <fa-icon [icon]="faGear" class="text-gray-500 hover:text-tq-primary-600"></fa-icon>
            </button>
            <a routerLink="/search" class="btn btn-primary btn-sm shadow-lg shadow-tq-primary-500/25
                                          hover:shadow-tq-glow transition-all duration-300">
              <fa-icon [icon]="faMagnifyingGlass"></fa-icon>
              Start Searching
            </a>
          </div>

          <!-- Mobile Menu Button -->
          <button 
            class="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
            (click)="toggleMobileMenu()"
            [attr.aria-expanded]="isMobileMenuOpen()"
            aria-label="Toggle menu">
            <fa-icon [icon]="isMobileMenuOpen() ? faXmark : faBars" 
                     class="text-xl text-gray-700"></fa-icon>
          </button>
        </div>

        <!-- Mobile Navigation -->
        @if (isMobileMenuOpen()) {
          <div class="md:hidden animate-fade-in-down">
            <div class="py-4 space-y-1 border-t border-gray-200">
              @for (item of navItems; track item.route) {
                <a [routerLink]="item.route" 
                   routerLinkActive="mobile-nav-link-active"
                   [routerLinkActiveOptions]="{exact: item.exact ?? false}"
                   class="mobile-nav-link"
                   (click)="closeMobileMenu()">
                  <fa-icon [icon]="item.icon" class="w-5"></fa-icon>
                  {{ item.label }}
                </a>
              }
              <div class="pt-4 mt-4 border-t border-gray-200">
                <a routerLink="/search" 
                   class="btn btn-primary w-full justify-center"
                   (click)="closeMobileMenu()">
                  <fa-icon [icon]="faMagnifyingGlass"></fa-icon>
                  Start Searching
                </a>
              </div>
            </div>
          </div>
        }
      </nav>
    </header>
    
    <!-- Spacer for fixed header -->
    <div class="h-16 md:h-20"></div>
  `,
  styles: [`
    .nav-link {
      @apply flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 
             rounded-lg transition-all duration-200
             hover:bg-tq-primary-50 hover:text-tq-primary-600;
    }
    
    .nav-link-active {
      @apply bg-tq-primary-50 text-tq-primary-600;
    }
    
    .mobile-nav-link {
      @apply flex items-center gap-3 px-4 py-3 text-base font-medium text-gray-700 
             rounded-lg transition-all duration-200
             hover:bg-tq-primary-50 hover:text-tq-primary-600;
    }
    
    .mobile-nav-link-active {
      @apply bg-tq-primary-50 text-tq-primary-600;
    }
  `]
})
export class HeaderComponent implements OnInit {
  // Icons
  faMagnifyingGlass = faMagnifyingGlass;
  faCloudArrowUp = faCloudArrowUp;
  faFileLines = faFileLines;
  faBars = faBars;
  faXmark = faXmark;
  faCircleQuestion = faCircleQuestion;
  faGear = faGear;
  faHome = faHome;

  // State
  isScrolled = signal(false);
  isMobileMenuOpen = signal(false);

  // Navigation items
  navItems: NavItem[] = [
    { label: 'Home', route: '/', icon: faHome, exact: true },
    { label: 'Search', route: '/search', icon: faMagnifyingGlass },
    { label: 'Transcripts', route: '/transcripts', icon: faFileLines },
    { label: 'Upload', route: '/upload', icon: faCloudArrowUp },
  ];

  ngOnInit(): void {
    this.checkScroll();
  }

  @HostListener('window:scroll')
  onWindowScroll(): void {
    this.checkScroll();
  }

  private checkScroll(): void {
    this.isScrolled.set(window.scrollY > 20);
  }

  toggleMobileMenu(): void {
    this.isMobileMenuOpen.update(value => !value);
  }

  closeMobileMenu(): void {
    this.isMobileMenuOpen.set(false);
  }
}