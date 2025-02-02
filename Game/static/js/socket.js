class GameSocket {
    constructor() {
        this.socket = io();
        this.lastEmit = Date.now();
        this.emitThrottle = 500; // Match game's update throttle
        this.setupSocketHandlers();
    }

    setupSocketHandlers() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
        });

        this.socket.on('game_state_update', (state) => {
            this.updateGameState(state);
        });

        // Send player position and score updates with throttling
        setInterval(() => {
            if (!game) return; // Wait for game to be initialized

            const now = Date.now();
            if (now - this.lastEmit > this.emitThrottle) {
                this.socket.emit('player_move', {
                    player_id: this.socket.id,
                    position: {
                        bin: game.activeBin,
                        binX: game.getCurrentBinX()
                    },
                    score: Math.floor(game.score),
                    itemsSorted: Math.floor(game.itemsSorted),
                    wasteReduced: Math.floor(game.wasteReduced)
                });
                this.lastEmit = now;
            }
        }, 50);
    }

    updateGameState(state) {
        if (!game) return; // Wait for game to be initialized

        // Update scores if they exist in the state with proper rounding
        if (state.scores && state.scores[this.socket.id]) {
            game.score = Math.floor(state.scores[this.socket.id]);
        }

        if (state.itemsSorted && state.itemsSorted[this.socket.id]) {
            game.itemsSorted = Math.floor(state.itemsSorted[this.socket.id]);
        }

        if (state.wasteReduced && state.wasteReduced[this.socket.id]) {
            game.wasteReduced = Math.floor(state.wasteReduced[this.socket.id]);
        }
    }
}

// Initialize socket connection after DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Wait a short moment for game to initialize
    setTimeout(() => {
        const gameSocket = new GameSocket();
    }, 100);
});