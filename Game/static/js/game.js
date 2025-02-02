// Create a global game instance
let game = null;
let animationFrameId = null;

class Game {
    constructor() {
        this.isInitialized = false;
        this.canvas = document.getElementById('gameCanvas');
        if (!this.canvas) {
            console.error('Canvas not found');
            return;
        }

        this.ctx = this.canvas.getContext('2d');
        this.playerBin = {
            x: 0,
            width: 60,
            height: 60,
            speed: 5
        };
        this.fallingItems = [];
        this.score = 0;
        this.itemsSorted = 0;
        this.wasteReduced = 0;
        this.lastScoreUpdate = Date.now();
        this.updateThrottle = 500;
        this.lastItemSpawn = Date.now();
        this.spawnInterval = 2500; // Increased from 1500 to 2500ms for slower spawn rate

        this.categories = [
            'Recyclables',
            'Compost',
            'Electronics',
            'Hazardous'
        ];

        this.categoryImpact = {
            'Recyclables': 'Catch all recyclable materials!',
            'Compost': 'Collect organic waste only!',
            'Electronics': 'Grab those electronics!',
            'Hazardous': 'Catch hazardous materials!'
        };

        this.currentCategory = this.categories[0];
        this.categoryChangeInterval = 15000; // 15 seconds per category

        // Load images with proper error handling
        this.loadImages().then(() => {
            this.initialize();
        }).catch(error => {
            console.error('Failed to load images:', error);
        });
    }

    async loadImages() {
        // Load bin image
        this.binImage = await this.loadImage('/static/images/recycling_bin.svg');

        // Load waste item images
        this.wasteImages = {
            'Recyclables': '/static/images/plastic.svg',
            'Compost': '/static/images/food_waste.svg',
            'Electronics': '/static/images/can.svg',
            'Hazardous': '/static/images/paper.svg'
        };

        this.loadedWasteImages = {};

        // Load all waste images
        await Promise.all(
            Object.entries(this.wasteImages).map(async ([category, src]) => {
                this.loadedWasteImages[category] = await this.loadImage(src);
            })
        );
    }

    loadImage(src) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = () => reject(new Error(`Failed to load image: ${src}`));
            img.src = src;
        });
    }

    initialize() {
        if (this.isInitialized) return;

        window.addEventListener('resize', () => this.resize());
        this.resize();
        this.startGameSystems();
        this.isInitialized = true;
        this.gameLoop();
    }

    cleanup() {
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
    }

    startGameSystems() {
        // Start category rotation
        setInterval(() => {
            const currentIndex = this.categories.indexOf(this.currentCategory);
            const nextIndex = (currentIndex + 1) % this.categories.length;
            this.currentCategory = this.categories[nextIndex];

            // Update DOM elements
            this.updateDOMElement('currentCategory', this.currentCategory);
            this.updateDOMElement('environmentalImpact', this.categoryImpact[this.currentCategory]);
        }, this.categoryChangeInterval);
    }

    updateDOMElement(id, text) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = text;
        }
    }

    resize() {
        if (!this.canvas) return;

        const container = this.canvas.parentElement;
        if (!container) return;

        this.canvas.width = container.clientWidth;
        this.canvas.height = Math.min(window.innerHeight * 0.6, 600);

        // Position bin at bottom center
        this.playerBin.x = (this.canvas.width - this.playerBin.width) / 2;
    }

    spawnItems() {
        const now = Date.now();
        if (now - this.lastItemSpawn > this.spawnInterval) {
            // 50% chance to spawn matching item
            const spawnMatchingItem = Math.random() < 0.5;
            const category = spawnMatchingItem ? this.currentCategory : 
                this.categories[Math.floor(Math.random() * this.categories.length)];

            this.fallingItems.push({
                x: Math.random() * (this.canvas.width - 40),
                y: 0,
                width: 40,
                height: 40,
                speed: 1.5, // Reduced from 3 to 1.5 for slower falling speed
                category: category,
                isMatching: category === this.currentCategory
            });

            this.lastItemSpawn = now;
        }
    }

    movePlayerBin(direction) {
        const newX = this.playerBin.x + (direction * this.playerBin.speed);
        this.playerBin.x = Math.max(0, Math.min(newX, this.canvas.width - this.playerBin.width));
    }

    updateItems() {
        this.spawnItems();

        this.fallingItems = this.fallingItems.filter(item => {
            item.y += item.speed;

            // Check collision with player bin
            if (item.y + item.height >= this.canvas.height - this.playerBin.height) {
                if (
                    item.x + item.width > this.playerBin.x && 
                    item.x < this.playerBin.x + this.playerBin.width
                ) {
                    if (item.category === this.currentCategory) {
                        // Caught matching item
                        this.score += 50;
                        this.wasteReduced += 100;
                        this.itemsSorted++;
                        this.showFeedback("✓ Correct!", this.playerBin.x + this.playerBin.width/2, this.canvas.height - 140, "#4CAF50");
                    } else {
                        // Caught wrong item
                        this.score = Math.max(0, this.score - 30);
                        this.showFeedback("✗ Wrong!", this.playerBin.x + this.playerBin.width/2, this.canvas.height - 140, "#F44336");
                    }
                    return false;
                }
            }

            // Remove items that fall off screen
            if (item.y > this.canvas.height) {
                if (item.category === this.currentCategory) {
                    // Penalty for missing matching item
                    this.score = Math.max(0, this.score - 20);
                    this.showFeedback("Missed!", item.x + item.width/2, this.canvas.height - 140, "#FFC107");
                }
                return false;
            }

            return true;
        });
    }

    showFeedback(text, x, y, color) {
        if (!this.ctx) return;

        this.ctx.save();
        this.ctx.font = 'bold 24px Inter';
        this.ctx.fillStyle = color;
        this.ctx.strokeStyle = '#000';
        this.ctx.lineWidth = 2;
        this.ctx.textAlign = 'center';
        this.ctx.shadowColor = 'rgba(0,0,0,0.5)';
        this.ctx.shadowBlur = 4;
        this.ctx.shadowOffsetX = 2;
        this.ctx.shadowOffsetY = 2;

        this.ctx.strokeText(text, x, y);
        this.ctx.fillText(text, x, y);
        this.ctx.restore();
    }

    update() {
        if (!this.isInitialized) return;
        this.updateItems();
    }

    draw() {
        if (!this.ctx || !this.canvas || !this.isInitialized) return;

        // Clear canvas with gradient background
        const gradient = this.ctx.createLinearGradient(0, 0, 0, this.canvas.height);
        gradient.addColorStop(0, '#1a1f2c');
        gradient.addColorStop(1, '#2d3748');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.drawGrid();

        // Draw current category indicator
        this.ctx.save();
        this.ctx.font = 'bold 32px Inter';
        this.ctx.fillStyle = '#4CAF50';
        this.ctx.textAlign = 'center';
        this.ctx.shadowColor = 'rgba(0,0,0,0.5)';
        this.ctx.shadowBlur = 4;
        this.ctx.fillText(`Collect: ${this.currentCategory}`, this.canvas.width / 2, 50);
        this.ctx.restore();

        // Draw player bin
        if (this.binImage) {
            this.ctx.save();
            this.ctx.shadowColor = '#4CAF50';
            this.ctx.shadowBlur = 20;
            this.ctx.drawImage(
                this.binImage,
                this.playerBin.x,
                this.canvas.height - this.playerBin.height,
                this.playerBin.width,
                this.playerBin.height
            );
            this.ctx.restore();
        }

        // Draw falling items
        this.fallingItems.forEach(item => {
            const img = this.loadedWasteImages[item.category];
            if (img) {
                this.ctx.save();

                // Add glow effect for matching items
                if (item.category === this.currentCategory) {
                    this.ctx.shadowColor = '#4CAF50';
                    this.ctx.shadowBlur = 20;
                }

                const scale = 1 + Math.sin(Date.now() * 0.005) * 0.05;
                const rotation = (Date.now() * 0.001 + item.x) % (Math.PI * 2);
                this.ctx.translate(item.x + item.width/2, item.y + item.height/2);
                this.ctx.rotate(rotation);
                this.ctx.scale(scale, scale);
                this.ctx.drawImage(img, -item.width/2, -item.height/2, item.width, item.height);
                this.ctx.restore();
            }
        });

        // Update stats
        const now = Date.now();
        if (now - this.lastScoreUpdate > this.updateThrottle) {
            const stats = {
                'totalScore': this.score,
                'techDeployed': this.itemsSorted,
                'score': this.score,
                'wasteReduced': this.wasteReduced,
                'itemsSorted': this.itemsSorted,
                'efficiency': this.itemsSorted > 0 
                    ? Math.min(100, Math.floor((this.score / (this.itemsSorted * 10)) * 100))
                    : 100
            };

            Object.entries(stats).forEach(([id, value]) => {
                this.updateDOMElement(id, typeof value === 'number' ? Math.floor(value) : value);
            });

            this.lastScoreUpdate = now;
        }
    }

    drawGrid() {
        if (!this.ctx || !this.canvas) return;

        this.ctx.strokeStyle = 'rgba(72, 187, 120, 0.1)';
        this.ctx.lineWidth = 1;
        const gridSize = 50;

        for(let x = 0; x < this.canvas.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }

        for(let y = 0; y < this.canvas.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }

    gameLoop() {
        if (!this.isInitialized) return;

        this.update();
        this.draw();
        animationFrameId = requestAnimationFrame(() => this.gameLoop());
    }
    
    getCurrentBinX() {
        return this.playerBin.x;
    }
}

// Initialize game when the DOM is fully loaded
window.addEventListener('load', () => {
    if (game) {
        game.cleanup();
    }
    game = new Game();
});