// Initialize controls after game is created
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (game) {
            const controls = new Controls(game);
        }
    }, 200);
});

class Controls {
    constructor(game) {
        this.game = game;
        this.keysPressed = new Set();
        this.setupKeyboardControls();
        this.setupRPiControls();

        // Movement animation
        this.animate = this.animate.bind(this);
        requestAnimationFrame(this.animate);

        // Joystick values
        this.leftJoystick = 0;
        this.rightJoystick = 0;
    }

    setupKeyboardControls() {
        document.addEventListener('keydown', (e) => {
            this.keysPressed.add(e.key);
            this.showKeyPress(e.key);
        });

        document.addEventListener('keyup', (e) => {
            this.keysPressed.delete(e.key);
            this.hideKeyPress(e.key);
        });
    }

    setupRPiControls() {
        const rpiSocket = io('http://localhost:5001');

        rpiSocket.on('connect', () => {
            console.log('Connected to Raspberry Pi controller server');
        });

        rpiSocket.on('joystick_input', (data) => {
            this.leftJoystick = data.leftJoystick;
            this.rightJoystick = data.rightJoystick;
        });

        rpiSocket.on('connect_error', (error) => {
            console.log('Raspberry Pi controller connection error:', error);
            console.log('Falling back to keyboard controls');
        });
    }

    showKeyPress(key) {
        const keyHint = document.querySelector('.key-hint');
        if (keyHint) {
            keyHint.style.backgroundColor = 'rgba(72, 187, 120, 0.4)';
            keyHint.style.transform = 'scale(1.1)';
        }
    }

    hideKeyPress(key) {
        const keyHint = document.querySelector('.key-hint');
        if (keyHint) {
            keyHint.style.backgroundColor = 'rgba(72, 187, 120, 0.2)';
            keyHint.style.transform = 'scale(1)';
        }
    }

    animate() {
        // Handle keyboard movement
        if (this.keysPressed.has('ArrowLeft') || this.keysPressed.has('a')) {
            this.game.movePlayerBin(-1);
        }
        if (this.keysPressed.has('ArrowRight') || this.keysPressed.has('d')) {
            this.game.movePlayerBin(1);
        }

        // Handle joystick movement
        if (Math.abs(this.leftJoystick) > 0.1) {
            this.game.movePlayerBin(this.leftJoystick);
        }
        if (Math.abs(this.rightJoystick) > 0.1) {
            this.game.movePlayerBin(this.rightJoystick);
        }

        requestAnimationFrame(this.animate);
    }
}