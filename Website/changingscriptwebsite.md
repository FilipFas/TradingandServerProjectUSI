# WHAT TO DO AFTER CHANGING SCRIPT OF WEBSITE.PY
Usually the main error is "error while attempting to bind on address ('0.0.0.0', 8000)": address already in use indicates that another process is already using port 8000. You need to free up this port or choose a different port for your FastAPI application.

### Identify the Process Using Port 8000
You can find out which process is using port 8000 with the following command:

```bash
sudo lsof -i :8000
```
This command will list the process using port 8000. You can then decide whether to stop that process or use a different port.

### Stop the Process Using Port 8000
If you want to stop the process using port 8000, note the PID (Process ID) from the output of the previous command and run:
```bash
sudo kill -9 <PID>
```
Replace <PID> with the actual process ID.

### Reload and Restart the Service
Reload systemd to apply the changes:
```bash
sudo systemctl daemon-reload
```
Restart the service:
```bash
sudo systemctl restart website.service
```
Enable the service to start on boot (if not already enabled):
```bash
sudo systemctl enable website.service
```
### Verify the Service
Check the status of the service to ensure it is running:
```bash
sudo systemctl status website.service
```
Check the logs for any errors:
```bash
sudo journalctl -u website.service -f
```
By following these steps, you can resolve the issue of the port being in use and ensure that your FastAPI application runs correctly as a systemd service.
