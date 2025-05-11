"""
Magic Survivor - UI Manager

This module handles the game's user interface components.
"""

import pygame
from src import config

class Button:
    """A simple button class for UI elements"""
    
    def __init__(self, x, y, width, height, text, color=config.GRAY, hover_color=config.WHITE, text_color=config.BLACK, font_size=20, on_click_data=None):
        """Initialize a button
        
        Args:
            x (int): X position of the button
            y (int): Y position of the button
            width (int): Width of the button
            height (int): Height of the button
            text (str): Text to display on the button
            color (tuple): RGB color tuple for the button
            hover_color (tuple): RGB color tuple for when the mouse hovers over the button
            text_color (tuple): RGB color tuple for the text
            font_size (int): Font size for the text
            on_click_data (any, optional): Data to associate with the button click. Defaults to None.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
        self.is_active = True
        self.on_click_data = on_click_data
    
    def update(self, mouse_pos):
        """Update the button's state
        
        Args:
            mouse_pos (tuple): Current mouse position (x, y)
        """
        if self.is_active:
            self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def render(self, screen):
        """Render the button
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        if not self.is_active:
            # Draw a dimmed button if inactive
            pygame.draw.rect(screen, (self.color[0] // 2, self.color[1] // 2, self.color[2] // 2), self.rect)
            pygame.draw.rect(screen, config.BLACK, self.rect, 2)  # Border
        else:
            # Draw normal or hovered button
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, config.BLACK, self.rect, 2)  # Border
        
        # Render text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, event):
        """Check if the button is clicked
        
        Args:
            event (pygame.event.Event): Mouse event
            
        Returns:
            bool: True if the button is clicked, False otherwise
        """
        if not self.is_active:
            return False
        
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and  # Left click
                self.rect.collidepoint(event.pos))


class ProgressBar:
    """A progress bar for displaying health, XP, etc."""
    
    def __init__(self, x, y, width, height, value=100, max_value=100, color=config.GREEN, background_color=config.GRAY, border_color=config.BLACK):
        """Initialize a progress bar
        
        Args:
            x (int): X position of the bar
            y (int): Y position of the bar
            width (int): Width of the bar
            height (int): Height of the bar
            value (float): Current value
            max_value (float): Maximum value
            color (tuple): RGB color tuple for the filled portion
            background_color (tuple): RGB color tuple for the background
            border_color (tuple): RGB color tuple for the border
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.value = value
        self.max_value = max_value
        self.color = color
        self.background_color = background_color
        self.border_color = border_color
    
    def update(self, value):
        """Update the progress bar's value
        
        Args:
            value (float): New value
        """
        self.value = min(max(0, value), self.max_value)
    
    def update_value(self, value):
        """Alias for update() - updates the progress bar's value
        
        Args:
            value (float): New value
        """
        self.update(value)
    
    def render(self, screen):
        """Render the progress bar
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Draw background
        pygame.draw.rect(screen, self.background_color, self.rect)
        
        # Draw filled portion
        fill_width = int(self.rect.width * (self.value / self.max_value))
        fill_rect = pygame.Rect(self.rect.left, self.rect.top, fill_width, self.rect.height)
        pygame.draw.rect(screen, self.color, fill_rect)
        
        # Draw border
        pygame.draw.rect(screen, self.border_color, self.rect, 2)


class TextBox:
    """A text box for displaying text"""
    
    def __init__(self, x, y, width, height, text="", font_size=20, text_color=config.BLACK, background_color=None, border_color=None, alignment="left"):
        """Initialize a text box
        
        Args:
            x (int): X position of the text box
            y (int): Y position of the text box
            width (int): Width of the text box
            height (int): Height of the text box
            text (str): Text to display
            font_size (int): Font size for the text
            text_color (tuple): RGB color tuple for the text
            background_color (tuple): RGB color tuple for the background (None for transparent)
            border_color (tuple): RGB color tuple for the border (None for no border)
            alignment (str): Text alignment ("left", "center", or "right")
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.text_color = text_color
        self.background_color = background_color
        self.border_color = border_color
        self.alignment = alignment
    
    def set_text(self, text):
        """Set the text
        
        Args:
            text (str): New text
        """
        self.text = text
    
    def render(self, screen):
        """Render the text box
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Draw background
        if self.background_color:
            pygame.draw.rect(screen, self.background_color, self.rect)
        
        # Draw border
        if self.border_color:
            pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # Render text
        # Wrap text to fit within the box
        words = self.text.split(' ')
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_surface = self.font.render(word, True, self.text_color)
            word_width = word_surface.get_width()
            
            if current_width + word_width <= self.rect.width:
                current_line.append(word)
                current_width += word_width + self.font.size(' ')[0]
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Render each line
        y_offset = 0
        for line in lines:
            line_surface = self.font.render(line, True, self.text_color)
            
            if self.alignment == "left":
                x_pos = self.rect.left
            elif self.alignment == "center":
                x_pos = self.rect.left + (self.rect.width - line_surface.get_width()) // 2
            else:  # "right"
                x_pos = self.rect.right - line_surface.get_width()
            
            screen.blit(line_surface, (x_pos, self.rect.top + y_offset))
            y_offset += line_surface.get_height()


class InputBox(TextBox):
    """A text box that allows user input"""

    def __init__(self, x, y, width, height, text="", font_size=20, text_color=config.BLACK, background_color=config.WHITE, border_color=config.BLACK, alignment="left", max_length=None):
        """Initialize an input box
        
        Args:
            x (int): X position of the input box
            y (int): Y position of the input box
            width (int): Width of the input box
            height (int): Height of the input box
            text (str): Initial text
            font_size (int): Font size for the text
            text_color (tuple): RGB color tuple for the text
            background_color (tuple): RGB color tuple for the background
            border_color (tuple): RGB color tuple for the border
            alignment (str): Text alignment ("left", "center", or "right")
            max_length (int, optional): Maximum number of characters. Defaults to None.
        """
        super().__init__(x, y, width, height, text, font_size, text_color, background_color, border_color, alignment)
        self.is_active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.max_length = max_length

    def handle_event(self, event):
        """Handle a single pygame event for the input box, assuming UIManager controls its active state.
        This method should only process KEYDOWN events if the box is active.
        
        Args:
            event (pygame.event.Event): The event to handle
        """
        if not self.is_active:
            return

        if event.type == pygame.KEYDOWN:
            # Ensure pygame.key.name is available, might need import pygame at top of file if not already. It is.
            print(f"DEBUG: InputBox Event: Active, Text='{self.text[:20]}', Key='{pygame.key.name(event.key)}', Unicode='{event.unicode}'")
            current_text_before_change = self.text
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                print(f"DEBUG: InputBox Text Change (Backspace): '{current_text_before_change}' -> '{self.text}'")
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Optionally, could trigger a "submit" or lose focus
                # If it loses focus, UIManager should be notified or handle it.
                # For now, let's make Enter deactivate it. UIManager will see is_active is false next frame.
                # Or better, UIManager handles deactivation on Enter explicitly if desired.
                # For now, just process text. Deactivation on Enter can be a feature later.
                pass # Or self.is_active = False; UIManager.active_input_box would need to be cleared.
            elif event.key == pygame.K_TAB:
                # Tab could be used to cycle focus, UIManager would handle this.
                pass
            else:
                if self.max_length is None or len(self.text) < self.max_length:
                    if event.unicode: # Only add if it's a printable character
                        self.text += event.unicode
                        print(f"DEBUG: InputBox Text Change (Add Char): '{current_text_before_change}' -> '{self.text}'")
            
            self.cursor_visible = True
            self.cursor_timer = 0

    def update_cursor(self, dt):
        """Update cursor visibility for blinking effect
        
        Args:
            dt (float): Time delta since last frame
        """
        if self.is_active:
            self.cursor_timer += dt
            if self.cursor_timer >= 0.5: # Blink every 0.5 seconds
                self.cursor_timer = 0
                self.cursor_visible = not self.cursor_visible

    def render(self, screen):
        """Render the input box
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        super().render(screen) # Render background and border from TextBox

        # Render text (TextBox.render() handles complex text wrapping, simplify for input)
        text_surface = self.font.render(self.text, True, self.text_color)
        
        # Text position based on alignment (simplified for single line input)
        text_x = self.rect.x + 5
        if self.alignment == "center":
            text_x = self.rect.centerx - text_surface.get_width() // 2
        elif self.alignment == "right":
            text_x = self.rect.right - text_surface.get_width() - 5
        
        text_y = self.rect.centery - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))

        if self.is_active and self.cursor_visible:
            cursor_x = text_x + text_surface.get_width()
            cursor_y_start = self.rect.top + 5
            cursor_y_end = self.rect.bottom - 5
            pygame.draw.line(screen, self.text_color, (cursor_x, cursor_y_start), (cursor_x, cursor_y_end), 1)
        
        # Draw a border to indicate focus
        if self.is_active:
            pygame.draw.rect(screen, config.BLUE, self.rect, 2) # Active border color


class UIManager:
    """Manages UI elements for the game"""
    
    def __init__(self):
        """Initialize the UI manager"""
        self.elements = {}  # Dict of {element_id: element}
        self.active_input_box = None
    
    def add_element(self, element_id, element):
        """Add a UI element
        
        Args:
            element_id (str): ID for the element
            element: UI element to add
        """
        self.elements[element_id] = element
    
    def remove_element(self, element_id):
        """Remove a UI element
        
        Args:
            element_id (str): ID of the element to remove
        """
        if element_id in self.elements:
            del self.elements[element_id]
    
    def get_element(self, element_id):
        """Get a UI element
        
        Args:
            element_id (str): ID of the element to get
            
        Returns:
            The UI element, or None if not found
        """
        return self.elements.get(element_id)
    
    def update(self, mouse_pos, events, dt):
        """Update all UI elements
        
        Args:
            mouse_pos (tuple): Current mouse position (x, y)
            events (list): List of pygame events
            dt (float): Time delta since last frame
            
        Returns:
            dict: Dictionary of {element_id: True} for elements that were clicked
        """
        clicked = {}
        clicked_on_ui_element_this_frame = False

        for element_id, element in self.elements.items():
            if isinstance(element, Button):
                element.update(mouse_pos)
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if element.is_clicked(event):
                            clicked[element_id] = True
                            clicked_on_ui_element_this_frame = True
                            if self.active_input_box:
                                self.active_input_box.is_active = False
                                self.active_input_box = None
            
            elif isinstance(element, InputBox):
                # Check for click on this InputBox first
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if element.rect.collidepoint(event.pos):
                            clicked_on_ui_element_this_frame = True
                            if self.active_input_box and self.active_input_box != element:
                                print(f"DEBUG: UIManager deactivating previous InputBox: {self.active_input_box}")
                                self.active_input_box.is_active = False
                            
                            print(f"DEBUG: UIManager activating InputBox: {element} (current text: '{element.text[:20]}')")
                            element.is_active = True
                            self.active_input_box = element
                            break

                if element.is_active:
                    for event_for_input_box in events:
                        element.handle_event(event_for_input_box)
                    element.update_cursor(dt)

        # Global deactivation: if a left-click occurred and it wasn't on any UI element handled above
        # or if it was on a different UI element that isn't an InputBox.
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not clicked_on_ui_element_this_frame and self.active_input_box:
                    # This means the click was on empty space
                    self.active_input_box.is_active = False
                    self.active_input_box = None
                # If click was on a UI element but it wasn't the active_input_box,
                # and that element was a button, it's already handled.
                # If it was another InputBox, it's also handled.
                # This logic ensures clicking outside deactivates.
        return clicked
    
    def render(self, screen):
        """Render all UI elements
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        for element in self.elements.values():
            element.render(screen)
        # Cursor update is now handled in UIManager.update when InputBox is active and dt is passed.


def create_health_bar(player):
    """Create a health bar for the player
    
    Args:
        player (Player): The player
        
    Returns:
        ProgressBar: The health bar
    """
    return ProgressBar(
        x=10,
        y=10,
        width=200,
        height=20,
        value=player.current_hp,
        max_value=player.max_hp,
        color=config.GREEN
    )


def create_xp_bar(player):
    """Create an XP bar for the player
    
    Args:
        player (Player): The player
        
    Returns:
        ProgressBar: The XP bar
    """
    return ProgressBar(
        x=10,
        y=40,
        width=200,
        height=10,
        value=player.xp,
        max_value=player.xp_to_next_level,
        color=config.BLUE
    )


def create_spell_ui(player, spells, x, y, width, height, spacing=10):
    """Create UI elements for spells
    
    Args:
        player (Player): The player
        spells (dict): Dictionary of {spell_id: Spell}
        x (int): X position of the spell UI
        y (int): Y position of the spell UI
        width (int): Width of each spell element
        height (int): Height of each spell element
        spacing (int): Spacing between spell elements
        
    Returns:
        dict: Dictionary of UI elements
    """
    ui_elements = {}
    
    # Create UI elements for each spell
    for i, (spell_id, spell) in enumerate(spells.items()):
        spell_x = x
        spell_y = y + i * (height + spacing)
        
        # Background rectangle
        ui_elements[f"spell_{spell_id}_bg"] = TextBox(
            x=spell_x,
            y=spell_y,
            width=width,
            height=height,
            background_color=config.GRAY,
            border_color=config.BLACK
        )
        
        # Spell name
        ui_elements[f"spell_{spell_id}_name"] = TextBox(
            x=spell_x + 5,
            y=spell_y + 5,
            width=width - 10,
            height=20,
            text=spell.name,
            text_color=config.BLACK,
            alignment="left"
        )
        
        # Spell level
        ui_elements[f"spell_{spell_id}_level"] = TextBox(
            x=spell_x + width - 30,
            y=spell_y + 5,
            width=25,
            height=20,
            text=f"Lv{spell.level}",
            text_color=config.BLACK,
            alignment="right"
        )
        
        # Spell description
        ui_elements[f"spell_{spell_id}_desc"] = TextBox(
            x=spell_x + 5,
            y=spell_y + 30,
            width=width - 10,
            height=height - 40,
            text=spell.description,
            text_color=config.BLACK,
            font_size=16,
            alignment="left"
        )
    
    return ui_elements


def create_relic_ui(player, relics, x, y, width, height, spacing=10):
    """Create UI elements for relics
    
    Args:
        player (Player): The player
        relics (dict): Dictionary of {relic_id: Relic}
        x (int): X position of the relic UI
        y (int): Y position of the relic UI
        width (int): Width of each relic element
        height (int): Height of each relic element
        spacing (int): Spacing between relic elements
        
    Returns:
        dict: Dictionary of UI elements
    """
    ui_elements = {}
    
    # Create UI elements for each relic
    for i, (relic_id, relic) in enumerate(relics.items()):
        relic_x = x
        relic_y = y + i * (height + spacing)
        
        # Background rectangle
        ui_elements[f"relic_{relic_id}_bg"] = TextBox(
            x=relic_x,
            y=relic_y,
            width=width,
            height=height,
            background_color=config.GRAY,
            border_color=config.BLACK
        )
        
        # Relic name
        ui_elements[f"relic_{relic_id}_name"] = TextBox(
            x=relic_x + 5,
            y=relic_y + 5,
            width=width - 10,
            height=20,
            text=relic.name,
            text_color=config.BLACK,
            alignment="left"
        )
        
        # Relic description
        ui_elements[f"relic_{relic_id}_desc"] = TextBox(
            x=relic_x + 5,
            y=relic_y + 30,
            width=width - 10,
            height=height - 40,
            text=relic.description,
            text_color=config.BLACK,
            font_size=16,
            alignment="left"
        )
    
    return ui_elements 