(function() {
    const floatBtn = document.getElementById('terminalApiFloat');
    const modal = document.getElementById('terminalModal');
    const closeBtn = document.getElementById('closeModal');
    const demoTerminal = document.getElementById('demoTerminal');
    
    const command = 'curl.exe https://sppucodes.vercel.app/api/cnl/16';
    let cmdIndex = 0;
    let typingInterval = null;
    let outputAdded = false;

    function typeCommand() {
        const typedCmd = document.getElementById('typedCmd');
        if (typedCmd && cmdIndex < command.length) {
            typedCmd.textContent += command[cmdIndex];
            cmdIndex++;
        } else {
            clearInterval(typingInterval);
            typingInterval = null;
            setTimeout(showOutput, 500);
        }
    }

    function showOutput() {
        // Check if output already exists to prevent duplicates
        if (outputAdded || demoTerminal.querySelector('.demo-output')) {
            return;
        }
        
        outputAdded = true;
        
        const demoCursor = document.getElementById('demoCursor');
        if (demoCursor) {
            demoCursor.style.display = 'none';
        }
        
        const output = `import socket

choice = input("Enter '1' for Domain to IP or '2' for IP to Domain: ")

if choice == '1':
    domain = input("Enter domain name: ")
    ip = socket.gethostbyname(domain)
    print("IP address of", domain, "is:", ip)

elif choice == '2':
    ip = input("Enter IP address: ")
    host = socket.gethostbyaddr(ip)
    print("Domain name of", ip, "is:", host[0])

else:
    print("Invalid choice.")`;
        
        // Add output after the command line
        const outputElement = document.createElement('div');
        outputElement.className = 'demo-output';
        outputElement.textContent = output;
        
        // Add new prompt line at the end (without blinking cursor)
        const newPrompt = document.createElement('div');
        newPrompt.className = 'demo-line';
        newPrompt.innerHTML = '<span class="demo-prompt">user@localhost:~$</span> ';
        
        demoTerminal.appendChild(outputElement);
        demoTerminal.appendChild(newPrompt);
    }

    function resetTerminal() {
        // Clear everything
        cmdIndex = 0;
        outputAdded = false;
        
        // Clear any running intervals
        if (typingInterval) {
            clearInterval(typingInterval);
            typingInterval = null;
        }
        
        // Reset terminal HTML
        demoTerminal.innerHTML = `
            <div class="demo-line">
                <span class="demo-prompt">user@localhost:~$</span> <span class="demo-command" id="typedCmd"></span><span class="demo-cursor" id="demoCursor"></span>
            </div>
        `;
    }

    function startDemo() {
        // Reset everything first
        resetTerminal();
        
        // Start typing after a delay
        setTimeout(() => {
            if (!typingInterval) {
                typingInterval = setInterval(typeCommand, 50);
            }
        }, 500);
    }

    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        
        // Stop any running animations
        if (typingInterval) {
            clearInterval(typingInterval);
            typingInterval = null;
        }
        
        // Reset for next time
        setTimeout(() => {
            resetTerminal();
        }, 300);
    }

    // Open modal
    floatBtn.addEventListener('click', () => {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        startDemo();
    });

    // Close modal button
    closeBtn.addEventListener('click', closeModal);

    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });
})();