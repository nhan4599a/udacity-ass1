# Write-up Template

### Analyze, choose, and justify the appropriate resource option for deploying the app.

*For **both** a VM or App Service solution for the CMS app:*
- *Analyze costs, scalability, availability, and workflow*
- *Choose the appropriate solution (VM or App Service) for deploying the app*
- *Justify your choice*

The most advantage of Azure VM orver Azure App Service is Azure VM give you the access to the underlying OS, with that, you can do some config to your OS to make your app run more effective, just to meet requirements. Another advantage of Azure VM is you can choose specialized CPU to maximize your app effective in some special situation which isn't supported yet by the Azure App Service. Along with these advantage, it have a very big disadvantage when compare to Azure App Service. It's more expense, more and more difficult to config scalibility and application deployment

The advantage of Azure App Service is it's simplifier than Azure VM to deploy application, more easier manage and config the scalibility and more chipper

In scenario of this app, Azure App Service is look like more suitable then the Azure VM because of the advantage of Azure App Service over Azure VM and also this app look like don't need the specialized CPU or OS configuration to run more effective

### Assess app changes that would change your decision.

*Detail how the app and any other needs would have to change for you to change your decision in the last section.* 

I will change to use Azure VM if this application run more effective on windows environment because look like Azure App Service with Python runtime is running on linux underlying. Or when this app have some features like availability to write report weekly to excel file, which is sometime require more configuration to OS level. Or maybe the app require more than 4 vCPUs, 14GB RAM or 250GB storage which is maximum hardware configuration of Azure App Service (Premium v2 P3V2) i will move to use Azure VM since it's allow me to attach an azure storage account instance to store your data which is much more bigger than 250GB of storage when azure storage account can be store up to 5PiB