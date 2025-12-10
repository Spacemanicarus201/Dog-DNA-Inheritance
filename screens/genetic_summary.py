import pygame
from logic.genetic_calculator import GeneticCalculator
from logic.phenotype_interpreter import PhenotypeInterpreter
from ui.button import Button
from utils.debug import debug  # <-- debugging enabled

class GeneticSummary:
    def __init__(self, app,
                 father_breed, mother_breed,
                 father_readable, mother_readable,
                 father_defaults, mother_defaults,
                 father_overrides, mother_overrides):

        debug("\n===== OPENING GENETIC SUMMARY SCREEN =====")
        self.app = app
        # store breeds so we can go back to the trait selection screen
        self.father_breed = father_breed
        self.mother_breed = mother_breed

        # Fonts
        self.font_title = pygame.font.SysFont(None, 32)
        self.font_header = pygame.font.SysFont(None, 26)
        self.font_normal = pygame.font.SysFont(None, 20)
        self.font_small = pygame.font.SysFont(None, 18)
        self.font_tiny = pygame.font.SysFont(None, 16)

        # Parent phenotype dicts
        self.father_readable = father_readable
        self.mother_readable = mother_readable

        # Genetic calculator
        self.calc = GeneticCalculator()
        self.father_genes = self.calc.combine_defaults_with_overrides(father_defaults, father_overrides)
        self.mother_genes = self.calc.combine_defaults_with_overrides(mother_defaults, mother_overrides)

        debug("Father final genotype:", self.father_genes)
        debug("Mother final genotype:", self.mother_genes)

        # Punnett + Monte Carlo + Bayesian + Similarity
        debug("→ Running genetic engine summary…")
        self.punnett, self.monte_samples, _ = self.calc.generate_summary(
            self.father_genes, self.mother_genes, samples=6
        )

        # Ensure each child has per-locus phenomap
        for child in self.monte_samples:
            geno = child["genotype"]
            child["phenomap"] = {
                locus: self.calc.genotype_to_readable({locus: alleles})[locus]
                for locus, alleles in geno.items()
            }

        debug("\n===== SUMMARY GENERATION DONE =====\n")

        # Scroll system
        self.scroll_y = 0
        self.scroll_speed = 50
        self.canvas_height = 3500
        self.canvas = pygame.Surface((self.app.WIDTH, self.canvas_height))

        # Logging flags
        self.logged = {"parents": False, "punnett": False, "monte": False}
        
        # DNA Exporter (lazy load)
        self.dna_exporter = None
        self.export_buttons = []  # Store export buttons for each puppy

        # Back button
        self.back_button = Button(
            (self.app.WIDTH // 2 - 80, self.app.HEIGHT - 60, 160, 48),
            "← Back",
            self.font_normal,
            self._go_back
        )

    def _go_back(self):
        debug("← Returning to TraitSelection screen")
        from screens.trait_selection import TraitSelection
        self.app.current_screen = TraitSelection(self.app, self.father_breed, self.mother_breed)
    
    def _export_puppy_dna(self, puppy_index):
        """Export a specific puppy's DNA to FASTA files."""
        debug(f"Exporting DNA for Puppy #{puppy_index + 1}")
        
        # Lazy load DNA exporter
        if self.dna_exporter is None:
            try:
                from Sequence.genotype_to_sequence import GenotypeToSequence
                from logic.dna_exporter import DNAExporter
                
                converter = GenotypeToSequence(
                    "Sequence/Reference.json",
                    "Sequence/extracted_genes"
                )
                self.dna_exporter = DNAExporter(converter)
            except Exception as e:
                debug(f"Failed to initialize DNA exporter: {e}")
                print(f"❌ Error: Could not load DNA sequences. Make sure gene files are extracted.")
                return
        
        # Get puppy data
        puppy = self.monte_samples[puppy_index]
        genotype = puppy["genotype"]
        
        # Get phenotype description
        description = PhenotypeInterpreter.get_full_description(genotype)
        
        try:
            # Export DNA files
            files = self.dna_exporter.export_puppy_dna(
                genotype, 
                puppy_index + 1,
                puppy_name=f"Puppy_{puppy_index + 1}"
            )
            
            # Create summary report
            report = self.dna_exporter.create_summary_report(
                genotype,
                puppy_index + 1,
                description,
                puppy_name=f"Puppy_{puppy_index + 1}"
            )
            
            print(f"\n✅ Exported Puppy #{puppy_index + 1} DNA!")
            print(f"   Files: {len(files)} gene sequences")
            print(f"   Report: {report}")
            print(f"   Location: exported_dna/\n")
            
        except Exception as e:
            debug(f"Export failed: {e}")
            print(f"❌ Export failed: {e}")

    # -----------------------------
    # Parents Table
    # -----------------------------
    def draw_parents(self, surf, y):
        if not self.logged["parents"]:
            debug("Drawing parent trait table…")
            self.logged["parents"] = True

        title = self.font_header.render("Parent Traits", True, (240,240,240))
        surf.blit(title, (self.app.WIDTH//2 - title.get_width()//2, y))
        y += 50

        # Create two side-by-side panels
        panel_width = (self.app.WIDTH - 180) // 2
        panel_height = 300
        left_x = 60
        right_x = self.app.WIDTH//2 + 30
        
        # Father panel
        pygame.draw.rect(surf, (40, 45, 55), (left_x, y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(surf, (100, 150, 200), (left_x, y, panel_width, panel_height), 2, border_radius=10)
        
        # Father header
        pygame.draw.rect(surf, (50, 80, 120), (left_x, y, panel_width, 35), border_radius=10)
        pygame.draw.rect(surf, (50, 80, 120), (left_x, y+18, panel_width, 17))
        father_label = self.font_normal.render(f"♂ Father ({self.father_breed})", True, (200, 230, 255))
        surf.blit(father_label, (left_x + 12, y + 8))
        
        # Mother panel
        pygame.draw.rect(surf, (40, 45, 55), (right_x, y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(surf, (200, 100, 150), (right_x, y, panel_width, panel_height), 2, border_radius=10)
        
        # Mother header
        pygame.draw.rect(surf, (120, 50, 80), (right_x, y, panel_width, 35), border_radius=10)
        pygame.draw.rect(surf, (120, 50, 80), (right_x, y+18, panel_width, 17))
        mother_label = self.font_normal.render(f"♀ Mother ({self.mother_breed})", True, (255, 200, 230))
        surf.blit(mother_label, (right_x + 12, y + 8))
        
        # Content area
        y_father = y + 45
        y_mother = y + 45

        f_items = list(self.father_readable.items())
        m_items = list(self.mother_readable.items())

        for i, (category, trait) in enumerate(f_items):
            # Alternate background for readability
            if i % 2 == 0:
                pygame.draw.rect(surf, (45, 50, 60), (left_x + 4, y_father - 2, panel_width - 8, 20))
            
            category_short = category.split("(")[0].strip()  # Remove locus info
            surf.blit(self.font_tiny.render(category_short, True, (150, 150, 150)), (left_x + 10, y_father))
            
            trait_text = self.font_small.render(trait, True, (230, 230, 230))
            surf.blit(trait_text, (left_x + 10, y_father + 12))
            y_father += 32

        for i, (category, trait) in enumerate(m_items):
            # Alternate background for readability
            if i % 2 == 0:
                pygame.draw.rect(surf, (45, 50, 60), (right_x + 4, y_mother - 2, panel_width - 8, 20))
            
            category_short = category.split("(")[0].strip()
            surf.blit(self.font_tiny.render(category_short, True, (150, 150, 150)), (right_x + 10, y_mother))
            
            trait_text = self.font_small.render(trait, True, (230, 230, 230))
            surf.blit(trait_text, (right_x + 10, y_mother + 12))
            y_mother += 32

        return y + panel_height + 20

    # -----------------------------
    # Punnett Square
    # -----------------------------
    def draw_punnett(self, surf, y):
        if not self.logged["punnett"]:
            debug("Drawing Punnett probability table…")
            self.logged["punnett"] = True

        title = self.font_header.render("Per Locus Probability", True, (240,240,180))
        surf.blit(title, (self.app.WIDTH//2 - title.get_width()//2, y))
        y += 45

        table_x = 60
        for locus, rows in self.punnett.items():
            surf.blit(self.font_normal.render(f"{locus} locus", True, (255,215,0)), (table_x, y))
            y += 26

            surf.blit(self.font_small.render("Genotype", True, (200,200,200)), (table_x, y))
            surf.blit(self.font_small.render("Prob", True, (200,200,200)), (table_x + 170, y))
            surf.blit(self.font_small.render("Trait", True, (200,200,200)), (table_x + 270, y))
            y += 18

            pygame.draw.line(surf, (100,100,100), (table_x, y), (table_x + 500, y), 1)
            y += 10

            for row in rows:
                surf.blit(self.font_small.render(row["genotype"], True, (235,235,235)), (table_x, y))
                surf.blit(self.font_small.render(row["probability"], True, (235,235,235)), (table_x + 170, y))
                surf.blit(self.font_small.render(row["trait"], True, (235,235,235)), (table_x + 270, y))
                y += 22

            y += 18
        return y

    # -----------------------------
    # Monte Carlo Vertical Cards
    # -----------------------------
    def draw_monte(self, surf, y):
        if not self.logged["monte"]:
            debug("Drawing Monte Carlo results (vertical card format)…")
            self.logged["monte"] = True

        title = self.font_header.render("Sample Offspring (Monte Carlo)", True, (180,255,255))
        surf.blit(title, (self.app.WIDTH//2 - title.get_width()//2, y))
        y += 45

        card_x = 60
        card_width = self.app.WIDTH - 120
        
        # Color scheme
        card_bg = (35, 38, 45)
        card_border = (80, 120, 160)
        header_bg = (45, 50, 60)
        
        interpreter = PhenotypeInterpreter()
        
        # Lazy load DNA converter (only once)
        if not hasattr(self, '_dna_converter'):
            try:
                from Sequence.genotype_to_sequence import GenotypeToSequence
                self._dna_converter = GenotypeToSequence(
                    "Sequence/Reference.json",
                    "Sequence/extracted_genes"
                )
                self._dna_available = True
            except Exception as e:
                debug(f"DNA sequences not available: {e}")
                self._dna_converter = None
                self._dna_available = False

        for i, child in enumerate(self.monte_samples, start=1):
            genotype = child["genotype"]
            phenomap = child["phenomap"]
            sims = child["similarity"]
            
            # Get human-readable description
            description = interpreter.get_full_description(genotype)
            simple_desc = interpreter.get_simple_description(genotype)

            # Calculate card height dynamically
            card_height = 240 if self._dna_available else 200  # Extra space for DNA
            
            # Draw card background
            pygame.draw.rect(surf, card_bg, (card_x, y, card_width, card_height), border_radius=12)
            pygame.draw.rect(surf, card_border, (card_x, y, card_width, card_height), 3, border_radius=12)
            
            # Header section with gradient-like effect
            pygame.draw.rect(surf, header_bg, (card_x, y, card_width, 40), border_radius=12)
            pygame.draw.rect(surf, header_bg, (card_x, y+20, card_width, 20))  # Overlap to flatten bottom
            
            # Card title
            title_text = self.font_normal.render(f"Puppy #{i}", True, (255, 220, 100))
            surf.blit(title_text, (card_x + 16, y + 10))
            
            y_offset = y + 50
            
            # Main description (human-readable)
            desc_color = (255, 255, 255)
            desc_lines = self.wrap_text(description, self.font_normal, card_width - 32)
            for line in desc_lines:
                surf.blit(self.font_normal.render(line, True, desc_color), (card_x + 16, y_offset))
                y_offset += 24
            
            y_offset += 8
            
            # Simple summary
            summary_text = self.font_small.render(f"Summary: {simple_desc}", True, (180, 220, 255))
            surf.blit(summary_text, (card_x + 16, y_offset))
            y_offset += 28
            
            # DNA Sequence Preview (first 25 bp)
            if self._dna_available and self._dna_converter:
                try:
                    dna_results = self._dna_converter.process_genotype(genotype)
                    
                    # Get first gene with sequence (usually MC1R)
                    if dna_results:
                        first_gene = list(dna_results.keys())[0]
                        sequence = dna_results[first_gene]['mutated_sequence']
                        preview = sequence[:25] if len(sequence) >= 25 else sequence
                        
                        # DNA preview label
                        dna_label = self.font_tiny.render(f"DNA Preview ({first_gene}):", True, (100, 200, 100))
                        surf.blit(dna_label, (card_x + 16, y_offset))
                        y_offset += 16
                        
                        # DNA sequence in monospace-style
                        dna_text = self.font_small.render(preview + "...", True, (150, 255, 150))
                        surf.blit(dna_text, (card_x + 16, y_offset))
                        y_offset += 22
                except Exception as e:
                    debug(f"Could not generate DNA preview for puppy {i}: {e}")
            
            # Similarity scores with icons
            sim_father = sims['father']
            sim_mother = sims['mother']
            
            # Father similarity
            father_color = (150, 200, 255) if sim_father > 0.5 else (180, 180, 180)
            father_text = self.font_small.render(
                f"♂ Father similarity: {sim_father:.0%}",
                True, father_color
            )
            surf.blit(father_text, (card_x + 16, y_offset))
            
            # Mother similarity
            mother_color = (255, 150, 200) if sim_mother > 0.5 else (180, 180, 180)
            mother_text = self.font_small.render(
                f"♀ Mother similarity: {sim_mother:.0%}",
                True, mother_color
            )
            surf.blit(mother_text, (card_x + card_width//2, y_offset))
            y_offset += 26
            
            # Genetic details (collapsible-style, smaller text)
            details_label = self.font_tiny.render("Genetic Details:", True, (150, 150, 150))
            surf.blit(details_label, (card_x + 16, y_offset))
            y_offset += 18
            
            # Show genotype in compact format
            genotype_parts = []
            for locus, alleles in genotype.items():
                genotype_parts.append(f"{locus}:{alleles[0]}/{alleles[1]}")
            
            genotype_str = "  ".join(genotype_parts)
            genotype_lines = self.wrap_text(genotype_str, self.font_tiny, card_width - 32)
            for line in genotype_lines:
                surf.blit(self.font_tiny.render(line, True, (130, 130, 130)), (card_x + 16, y_offset))
                y_offset += 14

            y += card_height + 16
        return y

    # -----------------------------
    # Helper: Wrap text for fixed-width cards
    # -----------------------------
    def wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    # -----------------------------
    # Build Canvas
    # -----------------------------
    def draw_canvas(self):
        self.canvas.fill((25,25,25))
        y = 30
        y = self.draw_parents(self.canvas, y) + 10
        y = self.draw_punnett(self.canvas, y) + 10
        y = self.draw_monte(self.canvas, y) + 50

    # -----------------------------
    # Scroll & Event Handling
    # -----------------------------
    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            prev_scroll = self.scroll_y
            self.scroll_y -= event.y * self.scroll_speed
            self.scroll_y = max(0, min(self.scroll_y, self.canvas_height - self.app.HEIGHT))
            if self.scroll_y != prev_scroll:
                debug(f"Scroll → {self.scroll_y}/{self.canvas_height - self.app.HEIGHT}")
        self.back_button.handle_event(event)

    # -----------------------------
    # Draw everything
    # -----------------------------
    def draw(self, screen):
        self.draw_canvas()
        screen.blit(self.canvas, (0, 0),
                    pygame.Rect(0, self.scroll_y, self.app.WIDTH, self.app.HEIGHT))

        # Scroll bar
        bar_x = self.app.WIDTH - 12
        bar_w = 8
        view_ratio = self.app.HEIGHT / self.canvas_height
        bar_h = int(self.app.HEIGHT * view_ratio)
        max_scroll = self.canvas_height - self.app.HEIGHT
        bar_y = int((self.scroll_y / max_scroll) * (self.app.HEIGHT - bar_h)) if max_scroll > 0 else 0
        pygame.draw.rect(screen, (70,70,70), (bar_x, 6, bar_w, self.app.HEIGHT-12))
        pygame.draw.rect(screen, (160,160,160), (bar_x, 6 + bar_y, bar_w, bar_h))

        self.back_button.draw(screen)
