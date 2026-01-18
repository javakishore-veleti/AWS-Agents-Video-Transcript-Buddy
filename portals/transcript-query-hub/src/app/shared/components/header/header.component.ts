import { Component, OnInit, HostListener, signal, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, NavigationEnd } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { filter } from 'rxjs/operators';
import { 
  faMagnifyingGlass, 
  faCloudArrowUp, 
  faFileLines,
  faBars,
  faXmark,
  faCircleQuestion,
  faGear,
  faHome,
  faUser,
  faRightFromBracket,
  faChartLine,
  faMessage,
  faComments
} from '@fortawesome/free-solid-svg-icons';
import { AuthService } from '../../../core/services';
import { ConversationService } from '../../../core/services/conversation.service';

interface NavItem {
  label: string;
  route: string;
  icon: any;
  exact?: boolean;
  matchPattern?: RegExp;  // Optional regex for custom matching
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
            @for (item of visibleNavItems(); track item.route) {
              <a [routerLink]="item.route" 
                 class="nav-link group"
                 [class.nav-link-active]="isRouteActive(item)">
                <fa-icon [icon]="item.icon" class="text-sm opacity-70 group-hover:opacity-100"></fa-icon>
                {{ item.label }}
              </a>
            }
          </div>

          <!-- Desktop Actions -->
          <div class="hidden md:flex items-center gap-3">
            @if (isAuthenticated()) {
              <!-- User Menu -->
              <div class="relative">
                <button 
                  (click)="toggleUserMenu()"
                  class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                  <div class="w-8 h-8 rounded-full bg-gradient-to-br from-tq-primary-600 to-tq-secondary-600 flex items-center justify-center">
                    <span class="text-white text-sm font-semibold">{{ getUserInitials() }}</span>
                  </div>
                  <div class="text-left">
                    <p class="text-sm font-medium text-gray-900">{{ user()?.email }}</p>
                    <p class="text-xs text-gray-500">{{ user()?.tier }}</p>
                  </div>
                </button>
                
                <!-- Dropdown -->
                @if (isUserMenuOpen()) {
                  <div class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                    <a routerLink="/usage" 
                       class="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                       (click)="closeUserMenu()">
                      <fa-icon [icon]="faChartLine"></fa-icon>
                      Usage & Billing
                    </a>
                    <button 
                      (click)="logout()"
                      class="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50">
                      <fa-icon [icon]="faRightFromBracket"></fa-icon>
                      Logout
                    </button>
                  </div>
                }
              </div>
            } @else {
              <!-- Login/Register Buttons -->
              <a routerLink="/login" class="text-sm font-medium text-gray-700 hover:text-tq-primary-600 transition-colors">
                Login
              </a>
              <a routerLink="/register" class="btn btn-primary btn-sm shadow-lg shadow-tq-primary-500/25
                                            hover:shadow-tq-glow transition-all duration-300">
                Get Started
              </a>
            }
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
              @for (item of visibleNavItems(); track item.route) {
                <a [routerLink]="item.route" 
                   class="mobile-nav-link"
                   [class.mobile-nav-link-active]="isRouteActive(item)"
                   (click)="closeMobileMenu()">
                  <fa-icon [icon]="item.icon" class="w-5"></fa-icon>
                  {{ item.label }}
                </a>
              }
              <div class="pt-4 mt-4 border-t border-gray-200 space-y-2">
                @if (isAuthenticated()) {
                  <a routerLink="/usage" 
                     class="btn btn-secondary w-full justify-center"
                     (click)="closeMobileMenu()">
                    <fa-icon [icon]="faChartLine"></fa-icon>
                    Usage & Billing
                  </a>
                  <button 
                    (click)="logout()"
                    class="btn btn-outline w-full justify-center text-red-600 border-red-600 hover:bg-red-50">
                    <fa-icon [icon]="faRightFromBracket"></fa-icon>
                    Logout
                  </button>
                } @else {
                  <a routerLink="/login" 
                     class="btn btn-secondary w-full justify-center"
                     (click)="closeMobileMenu()">
                    Login
                  </a>
                  <a routerLink="/register" 
                     class="btn btn-primary w-full justify-center"
                     (click)="closeMobileMenu()">
                    Get Started
                  </a>
                }
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
  private conversationService = inject(ConversationService);
  
  // Icons
  faMagnifyingGlass = faMagnifyingGlass;
  faCloudArrowUp = faCloudArrowUp;
  faFileLines = faFileLines;
  faBars = faBars;
  faXmark = faXmark;
  faCircleQuestion = faCircleQuestion;
  faGear = faGear;
  faHome = faHome;
  faUser = faUser;
  faRightFromBracket = faRightFromBracket;
  faChartLine = faChartLine;
  faMessage = faMessage;
  faComments = faComments;

  // State
  isScrolled = signal(false);
  isMobileMenuOpen = signal(false);
  isUserMenuOpen = signal(false);
  currentUrl = signal('');
  
  // Auth state
  isAuthenticated = this.authService.isAuthenticated;
  user = computed(() => this.authService.getCurrentUser());

  // Navigation items with custom match patterns
  // When a conversation is selected, upload/chat within it should highlight Conversations
  private allNavItems: NavItem[] = [
    { label: 'Home', route: '/', icon: faHome, exact: true },
    { label: 'Conversations', route: '/conversations', icon: faComments, matchPattern: /^\/conversations/ },
    { label: 'Search', route: '/search', icon: faMagnifyingGlass, exact: true },
    { label: 'Chat', route: '/chat', icon: faMessage, exact: true },
    { label: 'Transcripts', route: '/transcripts', icon: faFileLines },
    { label: 'Upload', route: '/upload', icon: faCloudArrowUp, exact: true },
  ];

  // Filter nav items based on auth state
  visibleNavItems = computed(() => {
    const authenticated = this.isAuthenticated();
    if (authenticated) {
      return this.allNavItems; // Show all items when logged in
    }
    return this.allNavItems.filter(item => item.route === '/'); // Only home when logged out
  });

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.checkScroll();
    
    // Track current URL for custom active state
    this.currentUrl.set(this.router.url);
    this.router.events.pipe(
      filter((event): event is NavigationEnd => event instanceof NavigationEnd)
    ).subscribe((event) => {
      this.currentUrl.set(event.urlAfterRedirects);
    });
  }

  @HostListener('window:scroll')
  onWindowScroll(): void {
    this.checkScroll();
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    // Close user menu when clicking outside
    const target = event.target as HTMLElement;
    if (!target.closest('.relative')) {
      this.isUserMenuOpen.set(false);
    }
  }

  private checkScroll(): void {
    this.isScrolled.set(window.scrollY > 20);
  }

  /**
   * Check if a nav item's route is currently active.
   * Uses custom matchPattern if defined, otherwise standard matching.
   * 
   * Special logic: When a conversation is selected and we're on upload/chat,
   * highlight Conversations instead of Upload/Chat standalone routes.
   */
  isRouteActive(item: NavItem): boolean {
    const url = this.currentUrl();
    const hasSelectedConversation = !!this.conversationService.selectedConversation();
    
    // If we're on a page that's part of a conversation workflow
    // (upload or chat with a selected conversation), highlight Conversations
    if (hasSelectedConversation) {
      const isConversationWorkflow = url === '/upload' || url === '/chat';
      
      if (item.route === '/conversations' && isConversationWorkflow) {
        return true;
      }
      
      if ((item.route === '/upload' || item.route === '/chat') && isConversationWorkflow) {
        return false;
      }
    }
    
    // Use custom match pattern if defined
    if (item.matchPattern) {
      return item.matchPattern.test(url);
    }
    
    // Standard exact or prefix matching
    if (item.exact) {
      return url === item.route;
    }
    
    return url.startsWith(item.route);
  }

  toggleMobileMenu(): void {
    this.isMobileMenuOpen.update(value => !value);
  }

  closeMobileMenu(): void {
    this.isMobileMenuOpen.set(false);
  }

  toggleUserMenu(): void {
    this.isUserMenuOpen.update(value => !value);
  }

  closeUserMenu(): void {
    this.isUserMenuOpen.set(false);
  }

  getUserInitials(): string {
    const email = this.user()?.email;
    if (!email) return 'U';
    return email.charAt(0).toUpperCase();
  }

  logout(): void {
    this.authService.logout();
    this.closeUserMenu();
    this.closeMobileMenu();
    this.router.navigate(['/']);
  }
}