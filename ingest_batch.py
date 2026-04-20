import yaml
from factories.component_factory import ComponentFactory

def run_batch_ingestion():
    print("--- Starting Slack Batch Ingestion ---")
    factory = ComponentFactory(config_path="config.yaml")
    
    # We must explicitly tell the factory to give us the Slack loader
    # (Assuming you updated get_ingestion_service to accept a loader name, or temporarily hardcode it)
    ingestion_service = factory.get_ingestion_service() 
    
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    channels = config["slack"]["target_channels"]
    
    for channel_id in channels:
        print(f"Processing Channel: {channel_id}")
        ingestion_service.process_file(channel_id) # Using process_file method, but passing channel ID
        
    print("Batch ingestion complete. ChromaDB is updated.")

if __name__ == "__main__":
    run_batch_ingestion()