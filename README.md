# EXIF-Dumper

**A simple tool for protecting your privacy**

*Project initialized on July 14, 2025, by @Masrkai*

---

## Why This Project Exists

This project was born from research into OSINT (Open Source Intelligence) techniques, specifically how images can be weaponized against users through embedded EXIF metadata. Most people don't realize that their photos contain a treasure trove of sensitive information that can be exploited by malicious actors.

### What EXIF Data Can Reveal

When you share an image, you might unknowingly be sharing:

- **GPS coordinates** - Exact location where the photo was taken
- **Device information** - Phone brand, model, and specifications
- **Camera settings** - ISO, aperture, shutter speed, flash usage
- **Timestamps** - Precise date and time of capture
- **Software details** - Apps used to edit or process the image

This metadata creates a detailed digital fingerprint that makes tracking you significantly easier. An attacker can determine what device you're using, where you've been, and build a profile of your daily patterns—all from seemingly innocent photos.

---

## The Solution

**EXIF-Dumper** provides a straightforward way to sanitize your images by editing, deleting, or patching EXIF data as needed. This tool ensures your personal information isn't inadvertently shared when you post photos online.

### Key Features

- **Metadata removal** - Strip all EXIF data from images
- **Selective editing** - Choose which data to keep or remove
- **Batch processing** - Handle multiple images at once
- **Privacy-focused** - No data collection or cloud processing

---

## Platform Support

**Currently supported:**
- Linux (all major distributions)

**Coming soon:**
- Windows
- macOS
- Mobile platforms

---

## "But Platforms Already Strip EXIF Data"

**This is a dangerous misconception.**

While some platforms like Instagram and Facebook claim to remove EXIF data, consider these critical points:

### Can You Trust Big Tech?

- These platforms often **extract and store** your location data before "removing" it
- They use this information for targeted advertising and user profiling
- Your data becomes part of their business model, not truly deleted

### The Reality of "Stripped" Data

Even when platforms remove EXIF data from public posts, they may:
- Keep the original files with full metadata on their servers
- Use the geolocation data for their own analytics
- Share this information with third parties or government agencies

**Taking control of your data *before* uploading is the only way to ensure true privacy.**

---


## Why Not Open Source licenses and going to make a new custom one?

simply put i wanted to try the custom licenses, and i hate how some services provided by big corporations make a big profit without contributing to the developers.. seen many times

so here is the deal,

As a developer
- you can contribute code but the product still is mine

As a User
- You can use the program

As a Company / Entity / Business if you have a revenue of 1000$+
- you have to license the program from @Masrkai

License:

```

Masrkai Personal Use License v1.0

Copyright (c) 2025 Masrkai

Permission is hereby granted, free of charge, to any individual obtaining a copy of this software and associated documentation files (the "Software"), to use the Software for PERSONAL and NON-COMMERCIAL purposes only, subject to the following conditions:

1. The Software shall not be modified, distributed, sublicensed, or used in any commercial product, service, or offering without prior written permission and a commercial license agreement with the copyright holder.

2. The Software may not be reverse engineered, copied, or altered in any way.

3. Ownership of the Software remains solely with Masrkai. No entity, company, institution, organization, or government may claim ownership, sublicense, or redistribute the Software without explicit agreement.

4. Any unauthorized commercial use, distribution, or modification will constitute a violation of this license and may be subject to legal action.

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

For commercial use or licensing, please contact:
[GitHub: https://github.com/Masrkai]


```
---

## "I Have Nothing to Hide"

This argument fundamentally misunderstands privacy rights.

**Privacy isn't about hiding wrongdoing—it's about maintaining control over your personal information.**

Consider this analogy: Would you be comfortable with a camera in your bedroom streaming to the outside world? Of course not. The same principle applies to your digital footprint.

### Why Privacy Matters

- **Personal safety** - Preventing stalking, harassment, or physical harm
- **Professional protection** - Avoiding discrimination or career damage
- **Family security** - Protecting loved ones from unwanted attention
- **Future freedom** - Ensuring today's data can't be used against you tomorrow

Privacy is a fundamental human right, not a privilege for those with "something to hide."

---

## Getting Started

Ready to take control of your image privacy? Check out the installation guide (comming soon) and start protecting your digital footprint today.

*Remember: Your privacy is your responsibility. Don't leave it to chance.*
