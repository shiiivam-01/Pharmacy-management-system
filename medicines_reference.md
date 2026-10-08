# Common Medicines Seed Data

289 medicines commonly sold in Indian pharmacies, for seeding the `medicines` table of the Pharmacy Management System.

## Notes for the AI agent

- This is **catalog data only**. Do not create batches or stock from it.
- Machine-readable copy: `medicines_seed.csv` (same data, UTF-8 with BOM). Prefer the CSV for the import script.
- `unit_price` is in **rupees**, a rough estimate and not an official MRP. Store as integer paise (rupees x 100) using `Decimal`, never `float`.
- `Rx` = `requires_prescription` (1 = prescription medicine, 0 = over the counter). It is a best-judgement value, not verified.
- `manufacturer` is intentionally empty. `tax_percent` is 0 and `reorder_level` is 30 for tablets/capsules/sachets/lozenges and 10 for other forms.
- Uniqueness key: (`name`, `form`, `strength`), compared case-insensitively. There are no duplicates in this file.
- `description` needs a `description TEXT` column on `medicines`. Update `docs/architecture.md` and `pms/schema.sql` first (see `AGENTS.md`).
- Descriptions are one-line summaries for a catalog, not medical advice.

## Columns

`name, generic_name, form, strength, category, manufacturer, unit_price, tax_percent, reorder_level, requires_prescription, description`

## Medicines by category

### Antacid & Ulcer (15)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 1 | Aluminium Hydroxide + Magnesium Hydroxide | Chewable Tablet | - | 0 | 1.6 | Chewable antacid for heartburn |
| 2 | Aluminium Hydroxide + Magnesium Hydroxide + Simethicone | Suspension | - | 0 | 120 | Quick relief from acidity, gas and heartburn |
| 3 | Esomeprazole | Tablet | 40mg | 1 | 13 | Treats reflux and ulcers |
| 4 | Famotidine | Tablet | 20mg | 1 | 3.5 | Reduces stomach acid |
| 5 | Lansoprazole | Capsule | 30mg | 1 | 9 | Treats acid reflux and ulcers |
| 6 | Omeprazole | Capsule | 20mg | 1 | 3.8 | Treats acidity, reflux and ulcers |
| 7 | Pantoprazole | Injection | 40mg | 1 | 32 | Injectable acid reducer for severe acidity |
| 8 | Pantoprazole | Tablet | 40mg | 1 | 8.5 | Reduces stomach acid for acidity and ulcers |
| 9 | Pantoprazole + Domperidone | Capsule SR | 40mg/30mg | 1 | 13 | For acidity with nausea or bloating |
| 10 | Rabeprazole | Tablet | 20mg | 1 | 8.5 | Reduces stomach acid |
| 11 | Rabeprazole + Domperidone | Capsule SR | 20mg/30mg | 1 | 13 | For acid reflux with nausea |
| 12 | Simethicone | Chewable Tablet | 40mg | 0 | 1.4 | Relieves gas and bloating |
| 13 | Simethicone | Oral Drops | 40mg/ml | 0 | 72 | Relieves infant colic and gas |
| 14 | Sodium Alginate + Sodium Bicarbonate + Calcium Carbonate | Suspension | - | 0 | 145 | Forms a barrier to relieve acid reflux |
| 15 | Sucralfate | Suspension | 1g/10ml | 1 | 135 | Coats and protects stomach ulcers |

### Antibiotic (39)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 16 | Amoxicillin | Capsule | 250mg | 1 | 3.5 | Penicillin antibiotic for throat, ear and chest infections |
| 17 | Amoxicillin | Capsule | 500mg | 1 | 6.5 | Penicillin antibiotic for common bacterial infections |
| 18 | Amoxicillin | Dry Syrup | 125mg/5ml | 1 | 58 | Children's antibiotic for ear and throat infections |
| 19 | Amoxicillin + Clavulanic Acid | Dry Syrup | 200mg/28.5mg per 5ml | 1 | 95 | Children's broad-spectrum antibiotic |
| 20 | Amoxicillin + Clavulanic Acid | Tablet | 250mg/125mg | 1 | 15 | Antibiotic for sinus, chest and skin infections |
| 21 | Amoxicillin + Clavulanic Acid | Tablet | 500mg/125mg | 1 | 22 | Broad-spectrum antibiotic for resistant infections |
| 22 | Azithromycin | Suspension | 200mg/5ml | 1 | 70 | Children's antibiotic for throat and chest infections |
| 23 | Azithromycin | Tablet | 250mg | 1 | 13 | Macrolide antibiotic for respiratory and skin infections |
| 24 | Azithromycin | Tablet | 500mg | 1 | 23 | Macrolide antibiotic, usually a short course |
| 25 | Cefadroxil | Capsule | 500mg | 1 | 12 | Cephalosporin for skin and urinary infections |
| 26 | Cefixime | Dry Syrup | 100mg/5ml | 1 | 85 | Children's cephalosporin antibiotic |
| 27 | Cefixime | Tablet | 200mg | 1 | 15 | Cephalosporin for typhoid, urinary and throat infections |
| 28 | Cefpodoxime | Tablet | 200mg | 1 | 22 | Cephalosporin for respiratory and urinary infections |
| 29 | Ceftriaxone | Injection | 1g | 1 | 42 | Injectable cephalosporin for serious infections |
| 30 | Ceftriaxone | Injection | 250mg | 1 | 22 | Injectable antibiotic for children |
| 31 | Cefuroxime | Tablet | 500mg | 1 | 42 | Cephalosporin for chest and ENT infections |
| 32 | Cephalexin | Capsule | 500mg | 1 | 9 | Cephalosporin for skin and soft-tissue infections |
| 33 | Ciprofloxacin | Tablet | 500mg | 1 | 4.5 | Fluoroquinolone for urinary and stomach infections |
| 34 | Ciprofloxacin + Tinidazole | Tablet | 500mg/600mg | 1 | 9.5 | Treats gut infections and diarrhoea |
| 35 | Clarithromycin | Tablet | 250mg | 1 | 16 | Macrolide antibiotic for chest and sinus infections |
| 36 | Clindamycin | Capsule | 300mg | 1 | 22 | For dental, bone and skin infections |
| 37 | Doxycycline | Capsule | 100mg | 1 | 5.5 | Tetracycline antibiotic for acne, chest and skin infections |
| 38 | Erythromycin | Tablet | 250mg | 1 | 6.5 | Alternative antibiotic for penicillin allergy |
| 39 | Framycetin | Cream | 1% | 1 | 62 | Antibiotic cream for cuts and infected wounds |
| 40 | Fusidic Acid | Cream | 2% | 1 | 160 | Cream for infected skin and wounds |
| 41 | Gentamicin | Injection | 80mg/2ml | 1 | 9 | Injectable antibiotic for severe bacterial infections |
| 42 | Levofloxacin | Tablet | 500mg | 1 | 11 | Fluoroquinolone for chest and sinus infections |
| 43 | Metronidazole | Suspension | 200mg/5ml | 1 | 48 | Children's treatment for amoebiasis and giardiasis |
| 44 | Metronidazole | Tablet | 400mg | 1 | 1.6 | For amoebic dysentery and anaerobic infections |
| 45 | Mupirocin | Ointment | 2% | 1 | 155 | For skin infections like impetigo and boils |
| 46 | Neomycin + Bacitracin | Ointment | - | 0 | 58 | First-aid ointment to prevent infection in minor cuts |
| 47 | Nitrofurantoin | Capsule | 100mg | 1 | 7 | For urinary tract infections |
| 48 | Norfloxacin + Tinidazole | Tablet | 400mg/600mg | 1 | 6.5 | Treats infectious diarrhoea and dysentery |
| 49 | Ofloxacin | Tablet | 200mg | 1 | 4.5 | Fluoroquinolone for urinary and gut infections |
| 50 | Ofloxacin + Ornidazole | Tablet | 200mg/500mg | 1 | 8.5 | Treats diarrhoea and dysentery |
| 51 | Ornidazole | Tablet | 500mg | 1 | 5.5 | For amoebic and bacterial gut infections |
| 52 | Sulfamethoxazole + Trimethoprim | Suspension | 200mg/40mg per 5ml | 1 | 52 | Children's treatment for urinary and ear infections |
| 53 | Sulfamethoxazole + Trimethoprim | Tablet | 800mg/160mg | 1 | 3.5 | For urinary, chest and gut infections |
| 54 | Tinidazole | Tablet | 500mg | 1 | 4.5 | For giardia, amoebiasis and vaginal infections |

### Antifungal (12)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 55 | Clotrimazole | Cream | 1% | 0 | 68 | For ringworm, athlete's foot and jock itch |
| 56 | Clotrimazole | Vaginal Pessary | 100mg | 1 | 16 | For vaginal yeast infection |
| 57 | Fluconazole | Tablet | 150mg | 1 | 26 | Single-dose treatment for vaginal and skin fungal infections |
| 58 | Fluconazole | Tablet | 200mg | 1 | 36 | For fungal infections of skin, mouth and nails |
| 59 | Itraconazole | Capsule | 100mg | 1 | 23 | For ringworm and nail fungal infections |
| 60 | Ketoconazole | Shampoo | 2% | 1 | 195 | Medicated shampoo for dandruff and scalp fungus |
| 61 | Luliconazole | Cream | 1% | 1 | 165 | Antifungal cream for ringworm and jock itch |
| 62 | Miconazole | Cream | 2% | 0 | 78 | For fungal skin infections |
| 63 | Nystatin | Oral Drops | 100000IU/ml | 1 | 62 | For oral thrush in infants |
| 64 | Sertaconazole | Cream | 2% | 1 | 155 | Antifungal cream for skin infections |
| 65 | Terbinafine | Cream | 1% | 0 | 105 | For athlete's foot and ringworm |
| 66 | Terbinafine | Tablet | 250mg | 1 | 21 | For ringworm, athlete's foot and nail fungus |

### Antiparasitic (9)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 67 | Albendazole | Suspension | 200mg/5ml | 1 | 28 | Children's dewormer |
| 68 | Albendazole | Tablet | 400mg | 1 | 12 | Dewormer for roundworm, hookworm and tapeworm |
| 69 | Artemether + Lumefantrine | Tablet | 80mg/480mg | 1 | 85 | Treats uncomplicated falciparum malaria |
| 70 | Benzyl Benzoate | Lotion | 25% | 1 | 95 | Lotion for scabies and lice |
| 71 | Chloroquine | Tablet | 250mg | 1 | 3 | Antimalarial for vivax malaria |
| 72 | Hydroxychloroquine | Tablet | 200mg | 1 | 9 | For malaria prevention and rheumatoid arthritis |
| 73 | Ivermectin | Tablet | 12mg | 1 | 26 | For scabies, lice and strongyloidiasis |
| 74 | Mebendazole | Tablet | 100mg | 1 | 5 | Dewormer for worm infections |
| 75 | Permethrin | Cream | 5% | 1 | 155 | Cream for scabies |

### Antiseptic & First Aid (5)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 76 | Chloroxylenol | Solution | 4.8% | 0 | 72 | Disinfectant for washing wounds when diluted |
| 77 | Hydrogen Peroxide | Solution | 6% | 0 | 28 | Cleans wounds and removes debris (dilute before use) |
| 78 | Isopropyl Alcohol | Solution | 70% | 0 | 42 | Skin and surface disinfectant |
| 79 | Povidone Iodine | Ointment | 5% | 0 | 58 | Antiseptic ointment for cuts and wounds |
| 80 | Povidone Iodine | Solution | 5% | 0 | 88 | Antiseptic solution for wounds and skin |

### Antiviral (3)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 81 | Acyclovir | Cream | 5% | 1 | 72 | Cream for cold sores |
| 82 | Acyclovir | Tablet | 400mg | 1 | 8.5 | For herpes, cold sores and chickenpox |
| 83 | Oseltamivir | Capsule | 75mg | 1 | 52 | Treats influenza (flu) |

### Ayurvedic & Herbal (6)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 84 | Ashwagandha | Tablet | 500mg | 0 | 6 | Herbal tablet for stress and stamina |
| 85 | Chyawanprash | Paste | 500g | 0 | 245 | Herbal tonic for immunity |
| 86 | Giloy (Guduchi) | Tablet | 500mg | 0 | 5 | Herbal tablet for immunity |
| 87 | Gripe Water | Syrup | - | 0 | 62 | Herbal remedy for infant colic and gas |
| 88 | Herbal Cough Syrup | Syrup | - | 0 | 90 | Herbal syrup for dry and mild cough |
| 89 | Triphala | Powder | 100g | 0 | 90 | Traditional digestive and laxative herbal powder |

### Blood Pressure (21)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 90 | Amlodipine | Tablet | 10mg | 1 | 3.2 | Higher dose for high blood pressure |
| 91 | Amlodipine | Tablet | 5mg | 1 | 1.7 | Calcium-channel blocker for high blood pressure and angina |
| 92 | Atenolol | Tablet | 50mg | 1 | 1.8 | Beta-blocker for blood pressure and heart rate |
| 93 | Bisoprolol | Tablet | 5mg | 1 | 5.5 | Beta-blocker for blood pressure and heart failure |
| 94 | Carvedilol | Tablet | 6.25mg | 1 | 3.5 | For heart failure and high blood pressure |
| 95 | Enalapril | Tablet | 5mg | 1 | 2.2 | ACE inhibitor for blood pressure and heart failure |
| 96 | Furosemide | Tablet | 40mg | 1 | 1.8 | Water tablet for swelling and heart failure |
| 97 | Hydrochlorothiazide | Tablet | 12.5mg | 1 | 1.8 | Mild water tablet for high blood pressure |
| 98 | Losartan | Tablet | 50mg | 1 | 3.8 | For high blood pressure and kidney protection |
| 99 | Losartan + Hydrochlorothiazide | Tablet | 50mg/12.5mg | 1 | 5 | Combination for high blood pressure |
| 100 | Metoprolol Succinate | Tablet ER | 50mg | 1 | 6 | Beta-blocker for blood pressure and angina |
| 101 | Metoprolol Tartrate | Tablet | 50mg | 1 | 3 | Beta-blocker for blood pressure and angina |
| 102 | Olmesartan | Tablet | 20mg | 1 | 7 | For high blood pressure |
| 103 | Propranolol | Tablet | 40mg | 1 | 1.8 | Beta-blocker for blood pressure, migraine and palpitations |
| 104 | Ramipril | Capsule | 2.5mg | 1 | 5.5 | ACE inhibitor for blood pressure and heart protection |
| 105 | Spironolactone | Tablet | 25mg | 1 | 4.5 | Water tablet for heart failure and swelling |
| 106 | Telmisartan | Tablet | 20mg | 1 | 3.5 | For high blood pressure |
| 107 | Telmisartan | Tablet | 40mg | 1 | 5 | For high blood pressure |
| 108 | Telmisartan + Amlodipine | Tablet | 40mg/5mg | 1 | 9 | Combination for high blood pressure |
| 109 | Telmisartan + Hydrochlorothiazide | Tablet | 40mg/12.5mg | 1 | 8 | Combination for high blood pressure |
| 110 | Torsemide | Tablet | 10mg | 1 | 5.5 | Water tablet for swelling |

### Cholesterol (6)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 111 | Atorvastatin | Tablet | 10mg | 1 | 4.5 | Lowers cholesterol |
| 112 | Atorvastatin | Tablet | 20mg | 1 | 7 | Lowers cholesterol |
| 113 | Atorvastatin | Tablet | 40mg | 1 | 10 | Lowers cholesterol |
| 114 | Fenofibrate | Tablet | 160mg | 1 | 9 | Lowers triglycerides |
| 115 | Rosuvastatin | Tablet | 10mg | 1 | 9 | Lowers cholesterol |
| 116 | Rosuvastatin | Tablet | 20mg | 1 | 13 | Lowers cholesterol |

### Cold & Allergy (19)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 117 | Cetirizine | Syrup | 5mg/5ml | 0 | 48 | Allergy relief for children |
| 118 | Cetirizine | Tablet | 10mg | 0 | 1.3 | Relieves sneezing, runny nose and itchy skin |
| 119 | Chlorpheniramine | Tablet | 4mg | 0 | 0.6 | Relieves sneezing and runny nose; may cause drowsiness |
| 120 | Fexofenadine | Tablet | 120mg | 0 | 8 | Non-sedating antihistamine for hay fever |
| 121 | Fexofenadine | Tablet | 180mg | 0 | 10.5 | Non-sedating antihistamine for hives and allergy |
| 122 | Fluticasone | Nasal Spray | 50mcg | 1 | 290 | Steroid nasal spray for allergic rhinitis |
| 123 | Levocetirizine | Syrup | 2.5mg/5ml | 0 | 65 | Allergy relief for children |
| 124 | Levocetirizine | Tablet | 5mg | 0 | 3.2 | Allergy and cold relief with low drowsiness |
| 125 | Loratadine | Tablet | 10mg | 0 | 3.5 | Non-sedating antihistamine for allergies |
| 126 | Menthol + Camphor + Eucalyptus | Ointment | - | 0 | 65 | Chest and nose rub for cold relief |
| 127 | Menthol + Eucalyptus | Inhalant | - | 0 | 70 | Inhaled for blocked nose and headache |
| 128 | Montelukast + Levocetirizine | Tablet | 10mg/5mg | 1 | 12 | For allergic rhinitis with mild asthma |
| 129 | Oxymetazoline | Nasal Spray | 0.05% | 0 | 95 | Fast nasal decongestant spray |
| 130 | Paracetamol + Phenylephrine + Chlorpheniramine | Tablet | 500mg/10mg/2mg | 0 | 2.8 | Cold relief: fever, blocked nose and sneezing |
| 131 | Pheniramine | Injection | 22.75mg/ml | 1 | 10 | Injectable antihistamine for allergic reactions |
| 132 | Pheniramine | Tablet | 25mg | 1 | 1.8 | Antihistamine for allergy and itching; causes drowsiness |
| 133 | Sodium Chloride | Nasal Drops | 0.65% | 0 | 55 | Saline drops to loosen nasal congestion |
| 134 | Xylometazoline | Nasal Drops | 0.05% | 0 | 50 | Blocked nose relief for children |
| 135 | Xylometazoline | Nasal Drops | 0.1% | 0 | 55 | Quick relief from a blocked nose (adults) |

### Constipation (4)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 136 | Bisacodyl | Tablet | 5mg | 0 | 1.2 | Stimulant laxative for occasional constipation |
| 137 | Lactulose | Solution | 10g/15ml | 0 | 195 | Gentle laxative for constipation |
| 138 | Liquid Paraffin + Milk of Magnesia | Emulsion | - | 0 | 125 | Laxative emulsion for constipation |
| 139 | Psyllium Husk (Isabgol) | Powder | 100g | 0 | 125 | Fibre supplement for constipation |

### Cough & Respiratory (15)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 140 | Ambroxol | Syrup | 30mg/5ml | 0 | 75 | Loosens mucus in productive cough |
| 141 | Ambroxol | Tablet | 30mg | 0 | 3.5 | Thins phlegm in chest congestion |
| 142 | Ambroxol + Levosalbutamol + Guaifenesin | Syrup | 30mg/1mg/50mg per 5ml | 1 | 125 | Cough with wheeze and chest congestion |
| 143 | Bromhexine | Syrup | 4mg/5ml | 0 | 65 | Expectorant for children and adults |
| 144 | Bromhexine | Tablet | 8mg | 0 | 2.2 | Helps clear mucus from the airways |
| 145 | Budesonide | Inhaler | 200mcg | 1 | 260 | Preventer inhaler for asthma |
| 146 | Budesonide | Nebulizer Solution | 0.5mg/2ml | 1 | 38 | Nebulizer steroid for asthma and croup |
| 147 | Budesonide + Formoterol | Inhaler | 200mcg/6mcg | 1 | 480 | Combination inhaler for asthma and COPD |
| 148 | Doxofylline | Tablet | 400mg | 1 | 8.5 | Bronchodilator for asthma and COPD |
| 149 | Guaifenesin | Syrup | 100mg/5ml | 0 | 75 | Expectorant that thins mucus |
| 150 | Ipratropium | Nebulizer Solution | 500mcg/2ml | 1 | 22 | Nebulizer for wheeze and COPD |
| 151 | Levosalbutamol | Inhaler | 50mcg | 1 | 195 | Quick-relief inhaler for asthma and COPD |
| 152 | Montelukast | Tablet | 10mg | 1 | 8 | Prevents asthma attacks and allergy symptoms |
| 153 | Salbutamol | Inhaler | 100mcg | 1 | 155 | Quick-relief inhaler for asthma attacks |
| 154 | Salbutamol | Tablet | 2mg | 1 | 1.2 | Relaxes airways in asthma and wheezing |

### Dental & Throat (5)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 155 | Amylmetacresol + Dichlorobenzyl Alcohol | Lozenge | - | 0 | 4 | Soothes sore throat |
| 156 | Benzydamine | Mouthwash | 0.15% | 0 | 105 | Eases sore throat and mouth pain |
| 157 | Chlorhexidine | Mouthwash | 0.2% | 0 | 92 | Antiseptic mouthwash for gum problems |
| 158 | Choline Salicylate | Gel | 8.7% | 0 | 75 | For mouth ulcers |
| 159 | Povidone Iodine | Gargle | 2% | 0 | 92 | Gargle for sore throat and mouth infections |

### Diabetes (15)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 160 | Dapagliflozin | Tablet | 10mg | 1 | 19 | Lowers blood sugar through urine glucose loss |
| 161 | Glibenclamide | Tablet | 5mg | 1 | 1.5 | Lowers blood sugar in type 2 diabetes |
| 162 | Gliclazide | Tablet | 80mg | 1 | 4.5 | Lowers blood sugar in type 2 diabetes |
| 163 | Glimepiride | Tablet | 1mg | 1 | 3.5 | Increases insulin release in type 2 diabetes |
| 164 | Glimepiride | Tablet | 2mg | 1 | 5.5 | Higher dose for type 2 diabetes |
| 165 | Glimepiride + Metformin | Tablet SR | 1mg/500mg | 1 | 6.5 | Combination for type 2 diabetes |
| 166 | Metformin | Tablet | 500mg | 1 | 1.6 | First-line medicine for type 2 diabetes |
| 167 | Metformin | Tablet SR | 1000mg | 1 | 4.5 | Sustained-release higher dose |
| 168 | Metformin | Tablet SR | 500mg | 1 | 2.4 | Sustained-release; gentler on the stomach |
| 169 | Pioglitazone | Tablet | 15mg | 1 | 4.5 | Improves insulin sensitivity |
| 170 | Sitagliptin | Tablet | 100mg | 1 | 32 | Higher dose for type 2 diabetes |
| 171 | Sitagliptin | Tablet | 50mg | 1 | 21 | Lowers blood sugar in type 2 diabetes |
| 172 | Teneligliptin | Tablet | 20mg | 1 | 9 | Lowers blood sugar in type 2 diabetes |
| 173 | Vildagliptin | Tablet | 50mg | 1 | 13 | Lowers blood sugar in type 2 diabetes |
| 174 | Voglibose | Tablet | 0.3mg | 1 | 9 | Reduces blood sugar rise after meals |

### Diarrhoea & Probiotic (7)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 175 | Bacillus clausii | Oral Suspension | 2 billion spores/5ml | 0 | 30 | Probiotic for diarrhoea and gut balance |
| 176 | Lactobacillus (Probiotic) | Capsule | - | 0 | 12 | Probiotic for gut health |
| 177 | Loperamide | Capsule | 2mg | 1 | 2.8 | Slows diarrhoea; not for diarrhoea with blood or fever |
| 178 | Oral Rehydration Salts (WHO) | Powder Sachet | 21.8g | 0 | 22 | Replaces fluids and salts lost in diarrhoea |
| 179 | Racecadotril | Capsule | 100mg | 1 | 19 | Reduces watery diarrhoea |
| 180 | Saccharomyces boulardii | Capsule | 250mg | 0 | 28 | Probiotic for antibiotic-related diarrhoea |
| 181 | Zinc Sulphate | Dispersible Tablet | 20mg | 0 | 3.5 | Shortens childhood diarrhoea |

### Emergency (1)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 182 | Adrenaline (Epinephrine) | Injection | 1mg/ml | 1 | 16 | For severe allergic reactions (anaphylaxis) |

### Eye & Ear (8)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 183 | Carboxymethylcellulose | Eye Drops | 0.5% | 0 | 115 | Lubricating drops for dry eyes |
| 184 | Chloramphenicol | Eye Drops | 0.5% | 1 | 28 | Antibiotic drops for eye infections |
| 185 | Ciprofloxacin | Eye/Ear Drops | 0.3% | 1 | 42 | Antibiotic drops for eye and ear infections |
| 186 | Moxifloxacin | Eye Drops | 0.5% | 1 | 95 | Antibiotic drops for eye infections |
| 187 | Ofloxacin | Ear Drops | 0.3% | 1 | 52 | Antibiotic drops for ear infections |
| 188 | Ofloxacin | Eye Drops | 0.3% | 1 | 48 | Antibiotic drops for eye infections |
| 189 | Olopatadine | Eye Drops | 0.1% | 1 | 135 | Relieves itchy, allergic eyes |
| 190 | Tobramycin | Eye Drops | 0.3% | 1 | 72 | Antibiotic drops for eye infections |

### Heart (9)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 191 | Aspirin | Tablet | 75mg | 0 | 1 | Low-dose blood thinner to prevent clots (use as advised) |
| 192 | Aspirin + Clopidogrel | Capsule | 75mg/75mg | 1 | 7.5 | Dual blood thinner for heart patients |
| 193 | Clopidogrel | Tablet | 75mg | 1 | 4.5 | Prevents blood clots after heart attack or stroke |
| 194 | Digoxin | Tablet | 0.25mg | 1 | 1.8 | For heart failure and irregular heartbeat |
| 195 | Isosorbide Dinitrate | Sublingual Tablet | 5mg | 1 | 1.8 | Dissolves under the tongue for angina |
| 196 | Isosorbide Mononitrate | Tablet | 20mg | 1 | 3.5 | Prevents angina chest pain |
| 197 | Ranolazine | Tablet ER | 500mg | 1 | 16 | For long-term angina |
| 198 | Trimetazidine | Tablet MR | 35mg | 1 | 6 | Helps prevent angina attacks |
| 199 | Warfarin | Tablet | 5mg | 1 | 2.5 | Blood thinner that needs regular monitoring |

### Liver & Digestive (1)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 200 | Ursodeoxycholic Acid | Tablet | 300mg | 1 | 28 | For gallstones and some liver conditions |

### Muscle & Bone (5)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 201 | Alendronate | Tablet | 70mg | 1 | 25 | Weekly tablet for osteoporosis |
| 202 | Calcitriol | Capsule | 0.25mcg | 1 | 6.5 | Active vitamin D for bone and calcium health |
| 203 | Diacerein | Capsule | 50mg | 1 | 7 | Eases joint pain and slows damage in osteoarthritis |
| 204 | Thiocolchicoside | Tablet | 4mg | 1 | 8.5 | Muscle relaxant for spasm and back pain |
| 205 | Tizanidine | Tablet | 2mg | 1 | 5 | Relieves muscle stiffness and spasm |

### Nausea & Vomiting (7)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 206 | Dimenhydrinate | Tablet | 50mg | 0 | 2.5 | Prevents motion sickness |
| 207 | Domperidone | Suspension | 1mg/ml | 1 | 62 | Children's anti-nausea suspension |
| 208 | Domperidone | Tablet | 10mg | 1 | 2.2 | Relieves nausea, bloating and fullness |
| 209 | Metoclopramide | Tablet | 10mg | 1 | 1.2 | Treats nausea and slow stomach emptying |
| 210 | Ondansetron | Injection | 4mg/2ml | 1 | 16 | Injectable anti-vomiting medicine |
| 211 | Ondansetron | Tablet | 4mg | 1 | 3.5 | Prevents and treats nausea and vomiting |
| 212 | Prochlorperazine | Tablet | 5mg | 1 | 2.5 | Treats vertigo, nausea and vomiting |

### Neuro & Vertigo (4)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 213 | Betahistine | Tablet | 16mg | 1 | 6 | Treats vertigo and Meniere's disease |
| 214 | Flunarizine | Tablet | 5mg | 1 | 3.5 | Prevents migraine and vertigo |
| 215 | Methylcobalamin | Tablet | 1500mcg | 0 | 7 | Vitamin B12 for nerve health and tingling |
| 216 | Sumatriptan | Tablet | 50mg | 1 | 28 | Treats migraine attacks |

### Pain & Fever (21)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 217 | Aceclofenac | Tablet | 100mg | 1 | 3.2 | Relieves pain and swelling in arthritis and sprains |
| 218 | Aceclofenac + Paracetamol | Tablet | 100mg/325mg | 1 | 4.2 | Combined relief for joint and muscle pain |
| 219 | Diclofenac | Gel | 1% | 0 | 85 | Applied on skin for muscle and joint pain |
| 220 | Diclofenac | Injection | 75mg/3ml | 1 | 14 | Injectable relief for severe pain |
| 221 | Diclofenac | Tablet | 50mg | 1 | 1.6 | Anti-inflammatory for joint, muscle and dental pain |
| 222 | Diclofenac + Methyl Salicylate + Menthol | Gel | - | 0 | 95 | Pain-relief gel for sprains and back pain |
| 223 | Diclofenac + Paracetamol | Tablet | 50mg/325mg | 1 | 3.2 | Pain and inflammation relief |
| 224 | Etoricoxib | Tablet | 60mg | 1 | 8.5 | Long-acting pain relief for arthritis |
| 225 | Etoricoxib | Tablet | 90mg | 1 | 11 | Stronger dose for acute joint pain |
| 226 | Ibuprofen | Suspension | 100mg/5ml | 0 | 60 | Pain and fever relief for children |
| 227 | Ibuprofen | Tablet | 400mg | 0 | 1.8 | Relieves pain, fever and inflammation |
| 228 | Ibuprofen + Paracetamol | Tablet | 400mg/325mg | 0 | 2.6 | Combined pain and fever relief |
| 229 | Ketorolac | Tablet | 10mg | 1 | 3.8 | Short-term relief of moderate to severe pain |
| 230 | Mefenamic Acid | Tablet | 250mg | 1 | 2 | Relief from toothache, period pain and general pain |
| 231 | Mefenamic Acid | Tablet | 500mg | 1 | 3.2 | Stronger dose for period and dental pain |
| 232 | Menthol + Methyl Salicylate | Balm | - | 0 | 45 | Rub-on balm for headache, body ache and sprains |
| 233 | Naproxen | Tablet | 250mg | 1 | 4.5 | Pain and inflammation relief for arthritis |
| 234 | Paracetamol | Oral Drops | 100mg/ml | 0 | 45 | Fever relief for infants |
| 235 | Paracetamol | Syrup | 125mg/5ml | 0 | 55 | Fever and pain relief for children |
| 236 | Paracetamol | Tablet | 500mg | 0 | 1.6 | Relieves mild to moderate pain and reduces fever |
| 237 | Paracetamol | Tablet | 650mg | 0 | 2.5 | Higher-strength tablet for pain and fever |

### Skin (11)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 238 | Adapalene | Gel | 0.1% | 1 | 125 | Treats acne |
| 239 | Benzoyl Peroxide | Gel | 2.5% | 1 | 95 | Treats acne |
| 240 | Betamethasone | Cream | 0.05% | 1 | 65 | Steroid cream for inflamed or itchy skin |
| 241 | Calamine | Lotion | - | 0 | 78 | Soothes itching, rashes and sunburn |
| 242 | Clindamycin | Gel | 1% | 1 | 125 | Treats acne |
| 243 | Clobetasol | Cream | 0.05% | 1 | 95 | Strong steroid cream for severe skin conditions |
| 244 | Hydrocortisone | Cream | 1% | 1 | 58 | Mild steroid for itching, rashes and eczema |
| 245 | Mometasone | Cream | 0.1% | 1 | 125 | Steroid cream for eczema and dermatitis |
| 246 | Petroleum Jelly | Jelly | - | 0 | 42 | Moisturises dry skin and cracked lips |
| 247 | Silver Sulfadiazine | Cream | 1% | 1 | 75 | Prevents infection in burns |
| 248 | Zinc Oxide | Cream | - | 0 | 72 | Barrier cream for nappy rash and irritated skin |

### Steroid (6)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 249 | Dexamethasone | Injection | 4mg/ml | 1 | 9 | Injectable steroid for severe allergy and inflammation |
| 250 | Dexamethasone | Tablet | 0.5mg | 1 | 1.2 | Steroid for allergy and inflammation |
| 251 | Methylprednisolone | Tablet | 4mg | 1 | 4.5 | Steroid for inflammation and allergy |
| 252 | Prednisolone | Tablet | 10mg | 1 | 2.2 | Steroid for allergy, asthma and inflammation |
| 253 | Prednisolone | Tablet | 20mg | 1 | 3.5 | Steroid for allergy, asthma and inflammation |
| 254 | Prednisolone | Tablet | 5mg | 1 | 1.4 | Steroid for allergy, asthma and inflammation |

### Stomach Cramps (4)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 255 | Dicyclomine | Tablet | 10mg | 1 | 2.2 | Relieves stomach cramps and IBS pain |
| 256 | Dicyclomine + Paracetamol | Tablet | 20mg/500mg | 1 | 4 | Relieves abdominal pain and cramps |
| 257 | Drotaverine | Tablet | 40mg | 1 | 3.5 | Relieves stomach and period cramps |
| 258 | Hyoscine Butylbromide | Tablet | 10mg | 1 | 6 | Relieves spasm-related stomach and period pain |

### Thyroid (4)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 259 | Carbimazole | Tablet | 5mg | 1 | 3 | For overactive thyroid |
| 260 | Levothyroxine | Tablet | 100mcg | 1 | 3.5 | Thyroid hormone replacement for hypothyroidism |
| 261 | Levothyroxine | Tablet | 25mcg | 1 | 1.8 | Thyroid hormone replacement for hypothyroidism |
| 262 | Levothyroxine | Tablet | 50mcg | 1 | 2.4 | Thyroid hormone replacement for hypothyroidism |

### Urinary (2)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 263 | Disodium Hydrogen Citrate | Syrup | - | 0 | 115 | Eases burning during urination |
| 264 | Tamsulosin | Capsule | 0.4mg | 1 | 8.5 | Eases urine flow in prostate enlargement |

### Vitamins & Supplements (19)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 265 | Calcium Carbonate + Vitamin D3 | Tablet | 500mg/250IU | 0 | 4.8 | Calcium and vitamin D for bones |
| 266 | Cholecalciferol (Vitamin D3) | Capsule | 60000IU | 0 | 27 | Weekly vitamin D for deficiency |
| 267 | Cholecalciferol (Vitamin D3) | Granules Sachet | 60000IU | 0 | 27 | Vitamin D sachet mixed in water or milk |
| 268 | Cholecalciferol (Vitamin D3) | Oral Drops | 400IU/ml | 0 | 85 | Daily vitamin D for infants |
| 269 | Ferrous Ascorbate + Folic Acid | Syrup | - | 0 | 115 | Iron syrup for anaemia |
| 270 | Ferrous Ascorbate + Folic Acid | Tablet | 100mg/1.5mg | 0 | 5 | Iron supplement for anaemia |
| 271 | Folic Acid | Tablet | 5mg | 0 | 1.2 | For folate deficiency and pregnancy planning |
| 272 | Iron + Folic Acid (IFA) | Tablet | 100mg/500mcg | 0 | 1.2 | Standard iron and folic acid tablet |
| 273 | Methylcobalamin | Injection | 1500mcg/ml | 1 | 28 | Injectable vitamin B12 for deficiency and neuropathy |
| 274 | Multivitamin | Oral Drops | - | 0 | 72 | Multivitamin drops for infants |
| 275 | Multivitamin | Syrup | - | 0 | 105 | Multivitamin syrup for children and adults |
| 276 | Multivitamin + Multimineral | Capsule | - | 0 | 8 | Daily multivitamin and mineral supplement |
| 277 | Omega-3 Fatty Acids | Capsule | 1000mg | 0 | 9 | Fish-oil supplement for heart health |
| 278 | Vitamin B-Complex | Syrup | - | 0 | 90 | B vitamins syrup for appetite and energy |
| 279 | Vitamin B-Complex | Tablet | - | 0 | 1.8 | Daily B vitamins for energy and nerves |
| 280 | Vitamin C | Chewable Tablet | 500mg | 0 | 2.2 | Vitamin C supplement |
| 281 | Vitamin E | Capsule | 400mg | 0 | 3.5 | Antioxidant vitamin supplement |
| 282 | Zinc Sulphate | Syrup | 20mg/5ml | 0 | 62 | Zinc supplement for children |
| 283 | Zinc Sulphate | Tablet | 20mg | 0 | 3.5 | Zinc supplement for immunity and healing |

### Women's Health (6)

| # | Medicine | Form | Strength | Rx | Price (Rs.) | Description |
|---|---|---|---|---|---|---|
| 284 | Levonorgestrel | Tablet | 1.5mg | 0 | 105 | Emergency contraceptive pill; take as soon as possible |
| 285 | Levonorgestrel + Ethinylestradiol | Tablet | 0.15mg/0.03mg | 1 | 5 | Combined oral contraceptive pill |
| 286 | Medroxyprogesterone | Tablet | 10mg | 1 | 19 | Regulates periods and treats abnormal bleeding |
| 287 | Norethisterone | Tablet | 5mg | 1 | 5.5 | Delays or regulates periods |
| 288 | Progesterone | Capsule | 200mg | 1 | 32 | Hormone support in some pregnancy and cycle problems |
| 289 | Tranexamic Acid | Tablet | 500mg | 1 | 16 | Reduces heavy menstrual bleeding |
