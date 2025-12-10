import pygame


class SearchTable:
    """
    A searchable table/list UI component with:
    - Search input field for filtering
    - Scrollable list of items
    - Click selection with highlighting
    """
    
    def __init__(self, rect, items, font, on_select_callback, color=(100, 150, 255)):
        """
        Args:
            rect: (x, y, width, height) for the entire component
            items: List of strings to display
            font: pygame font for rendering text
            on_select_callback: Function to call when an item is selected (receives item string)
            color: RGB tuple for the component's accent color
        """
        self.rect = pygame.Rect(rect)
        self.items = items
        self.all_items = items.copy()  # Keep original list
        self.font = font
        self.on_select_callback = on_select_callback
        self.color = color
        
        # Search state
        self.search_text = ""
        self.search_active = False
        
        # Selection state
        self.selected_item = None
        
        # Scroll state
        self.scroll_offset = 0
        self.item_height = 35
        self.visible_items = 10  # Will be recalculated based on height
        
        # Layout (will be set in resize)
        self.search_rect = None
        self.list_rect = None
        
        self._calculate_layout()
    
    def _calculate_layout(self):
        """Calculate positions of search box and list area"""
        padding = 5
        search_height = 40
        
        # Search box at top
        self.search_rect = pygame.Rect(
            self.rect.x + padding,
            self.rect.y + padding,
            self.rect.width - 2 * padding,
            search_height
        )
        
        # List area below search
        list_y = self.search_rect.bottom + padding
        list_height = self.rect.height - search_height - 3 * padding
        
        self.list_rect = pygame.Rect(
            self.rect.x + padding,
            list_y,
            self.rect.width - 2 * padding - 20,  # Leave space for scrollbar
            list_height
        )
        
        # Calculate how many items fit
        self.visible_items = max(1, list_height // self.item_height)
    
    def resize(self, rect):
        """Update component size and recalculate layout"""
        self.rect = pygame.Rect(rect)
        self._calculate_layout()
    
    def filter_items(self):
        """Filter items based on search text"""
        if not self.search_text:
            self.items = self.all_items.copy()
        else:
            search_lower = self.search_text.lower()
            self.items = [item for item in self.all_items if search_lower in item.lower()]
        
        # Reset scroll when filter changes
        self.scroll_offset = 0
    
    def handle_event(self, event):
        """Handle mouse and keyboard events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked on search box
            if self.search_rect.collidepoint(event.pos):
                self.search_active = True
            else:
                self.search_active = False
                
                # Check if clicked on an item in the list
                if self.list_rect.collidepoint(event.pos):
                    relative_y = event.pos[1] - self.list_rect.y
                    clicked_index = (relative_y // self.item_height) + self.scroll_offset
                    
                    if 0 <= clicked_index < len(self.items):
                        self.selected_item = self.items[clicked_index]
                        if self.on_select_callback:
                            self.on_select_callback(self.selected_item)
            
            # Handle scroll wheel (only if mouse is over this table)
            if self.rect.collidepoint(event.pos):
                if event.button == 4:  # Scroll up
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                elif event.button == 5:  # Scroll down
                    max_scroll = max(0, len(self.items) - self.visible_items)
                    self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
        
        elif event.type == pygame.KEYDOWN and self.search_active:
            if event.key == pygame.K_BACKSPACE:
                self.search_text = self.search_text[:-1]
                self.filter_items()
            elif event.key == pygame.K_RETURN:
                self.search_active = False
            elif event.unicode.isprintable():
                self.search_text += event.unicode
                self.filter_items()
    
    def draw(self, screen):
        """Draw the search table component"""
        # Draw search box
        search_bg_color = (60, 60, 60) if self.search_active else (40, 40, 40)
        pygame.draw.rect(screen, search_bg_color, self.search_rect, border_radius=8)
        pygame.draw.rect(screen, self.color if self.search_active else (100, 100, 100), 
                        self.search_rect, 2, border_radius=8)
        
        # Draw search text or placeholder
        if self.search_text:
            search_surface = self.font.render(self.search_text, True, (255, 255, 255))
        else:
            search_surface = self.font.render("Search...", True, (120, 120, 120))
        
        screen.blit(search_surface, (self.search_rect.x + 10, self.search_rect.y + 10))
        
        # Draw list background
        pygame.draw.rect(screen, (30, 30, 30), self.list_rect, border_radius=8)
        pygame.draw.rect(screen, (80, 80, 80), self.list_rect, 1, border_radius=8)
        
        # Draw visible items
        visible_items = self.items[self.scroll_offset:self.scroll_offset + self.visible_items]
        
        for i, item in enumerate(visible_items):
            item_y = self.list_rect.y + i * self.item_height
            item_rect = pygame.Rect(self.list_rect.x, item_y, self.list_rect.width, self.item_height)
            
            # Highlight selected item
            if item == self.selected_item:
                pygame.draw.rect(screen, self.color, item_rect, border_radius=6)
            
            # Highlight on hover
            mouse_pos = pygame.mouse.get_pos()
            if item_rect.collidepoint(mouse_pos):
                hover_color = tuple(min(c + 20, 255) for c in (40, 40, 40))
                pygame.draw.rect(screen, hover_color, item_rect, border_radius=6)
            
            # Draw item text
            text_color = (255, 255, 255) if item == self.selected_item else (200, 200, 200)
            text_surface = self.font.render(item, True, text_color)
            screen.blit(text_surface, (item_rect.x + 10, item_rect.y + 8))
        
        # Draw scrollbar if needed
        if len(self.items) > self.visible_items:
            scrollbar_x = self.list_rect.right + 5
            scrollbar_height = self.list_rect.height
            scrollbar_rect = pygame.Rect(scrollbar_x, self.list_rect.y, 10, scrollbar_height)
            
            # Scrollbar background
            pygame.draw.rect(screen, (50, 50, 50), scrollbar_rect, border_radius=5)
            
            # Scrollbar thumb
            thumb_height = max(20, scrollbar_height * self.visible_items / len(self.items))
            thumb_y = self.list_rect.y + (scrollbar_height - thumb_height) * (self.scroll_offset / max(1, len(self.items) - self.visible_items))
            thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 10, thumb_height)
            pygame.draw.rect(screen, self.color, thumb_rect, border_radius=5)
