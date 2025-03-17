#!/usr/bin/env python3
import logging
import os
import sys
import yaml
import asyncio
import signal
from pathlib import Path
from typing import Dict, Optional

from src.core.neural_network import NeuralNetwork
from src.core.quantum_processor import OptimizedQuantumProcessor
from src.core.hybrid_network import HybridNetwork
from src.interface.cli import CLI
from src.data.collector import DataCollector
from src.memory.memory_manager import MemoryManager
from src.learning.continuous_learner import ContinuousLearner

class ApplicationError(Exception):
    """Custom exception for application errors"""
    pass

class ApplicationContext:
    """Application Context Manager"""
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.config_file = self.base_dir / "config" / "config.yml"
        self.log_file = self.base_dir / "logs" / "app.log"
        
        # Components
        self.neural_network: Optional[NeuralNetwork] = None
        self.quantum_processor: Optional[OptimizedQuantumProcessor] = None
        self.hybrid_network: Optional[HybridNetwork] = None
        self.memory_manager: Optional[MemoryManager] = None
        self.data_collector: Optional[DataCollector] = None
        self.continuous_learner: Optional[ContinuousLearner] = None
        self.cli: Optional[CLI] = None
        
        # State
        self.logger: Optional[logging.Logger] = None
        self.running: bool = True
        self.config: Dict = {}
        self.learning_task: Optional[asyncio.Task] = None

    def load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            if not self.config_file.exists():
                raise FileNotFoundError(f"Configuration file not found at {self.config_file}")
                
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                
            if not config:
                raise ValueError("Configuration file is empty")
                
            return config
            
        except Exception as e:
            raise ApplicationError(f"Error loading configuration: {str(e)}")

    async def initialize(self) -> None:
        """Initialize application components"""
        try:
            # Load configuration
            self.config = self.load_config()
            
            # Initialize components
            self.memory_manager = MemoryManager()
            
            # Initialize Neural Network
            neural_config = self.config.get("neural_config", {})
            self.neural_network = NeuralNetwork(
                input_size=neural_config.get("input_size", 784),
                hidden_size=neural_config.get("hidden_size", 256),
                output_size=neural_config.get("output_size", 10),
                dropout_rate=neural_config.get("dropout_rate", 0.2)
            )
            
            # Initialize Quantum Processor
            quantum_config = self.config.get("quantum_config", {})
            self.quantum_processor = OptimizedQuantumProcessor(
                n_qubits=quantum_config.get("num_qubits", 4)
            )
            
            # Initialize Hybrid Network
            hybrid_config = self.config.get("hybrid_config", {})
            self.hybrid_network = HybridNetwork(
                n_qubits=quantum_config.get("num_qubits", 4),
                quantum_depth=hybrid_config.get("quantum_depth", 3),
                fusion_mode=hybrid_config.get("fusion_mode", "attention"),
                quantum_weight=hybrid_config.get("quantum_weight", 0.5),
                max_retries=hybrid_config.get("max_retries", 3),
                timeout=hybrid_config.get("timeout", 30),
                mixed_precision=hybrid_config.get("mixed_precision", True)
            )
            
            # Initialize Data Collector
            self.data_collector = DataCollector(self.memory_manager)
            
            # Initialize Continuous Learner
            self.continuous_learner = ContinuousLearner(
                hybrid_network=self.hybrid_network,
                memory_manager=self.memory_manager,
                collector=self.data_collector
            )
            
            # Start continuous learning
            self.learning_task = asyncio.create_task(
                self.continuous_learner.start_learning_loop()
            )
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Initialization error: {str(e)}")
            raise ApplicationError(f"Error during initialization: {str(e)}")

    async def shutdown(self) -> None:
        """Shutdown application components"""
        self.running = False
        
        if self.learning_task:
            self.learning_task.cancel()
            try:
                await self.learning_task
            except asyncio.CancelledError:
                pass
                
        if self.continuous_learner:
            self.continuous_learner.stop()
            
        if self.data_collector:
            await self.data_collector.stop()
            
        if self.cli:
            self.logger.info("CLI stopped")

def setup_logging(config: Dict) -> None:
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_level = config.get("log_level", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/app.log")
        ]
    )

async def signal_handler(signum: int, frame, app_context: ApplicationContext) -> None:
    """Handle system signals"""
    if app_context.logger:
        app_context.logger.info(f"Signal received: {signum}")
    await app_context.shutdown()

async def main() -> int:
    """Main application entry point"""
    app_context = ApplicationContext()
    
    try:
        # Initialize application
        await app_context.initialize()
        
        # Setup logging
        setup_logging(app_context.config)
        app_context.logger = logging.getLogger(__name__)
        app_context.logger.info("Starting application...")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, 
            lambda s, f: asyncio.create_task(signal_handler(s, f, app_context)))
        signal.signal(signal.SIGTERM, 
            lambda s, f: asyncio.create_task(signal_handler(s, f, app_context)))
        
        # Initialize CLI
        app_context.cli = CLI()
        app_context.logger.info("Application started successfully")
        
        # Main application loop
        while app_context.running:
            try:
                app_context.cli.cmdloop()  # Use cmdloop instead of run
                await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                app_context.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                app_context.logger.error(f"Error in main loop: {str(e)}")
                break
        
        app_context.logger.info("Normal application shutdown")
        return 0
        
    except ApplicationError as e:
        if app_context.logger:
            app_context.logger.error(str(e))
        return 1
    except Exception as e:
        if app_context.logger:
            app_context.logger.error(f"Unhandled error: {str(e)}")
        return 2
    finally:
        await app_context.shutdown()

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
