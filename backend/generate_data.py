import csv
import random

# --- Configuration ---
NUM_NORMAL_TRANSACTIONS = 1000
OUTPUT_FILE = 'large_test_data.csv'
# ---------------------

CATEGORIES = ['Shopping', 'Dining', 'Groceries', 'Travel', 'Utilities', 'Entertainment', 'Health', 'Services']
HEADERS = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount', 'Category', 'Class']

# --- Real Anomalies (taken from the original Kaggle dataset) ---
# We have manually added a 'Category' to each of these known fraudulent transactions.
REAL_ANOMALIES = [
    [406, -2.312226542, 1.951992011, -1.609850732, 3.997905588, -0.522187865, -1.426545319, -2.537387306, 1.391657248, -2.770089273, -2.772272145, 3.202033207, -2.899907388, -0.595221881, -4.289253782, 0.38972412, -1.14074718, -2.830055675, -0.016822468, 0.416955705, 0.126910559, 0.517232371, -0.035049369, -0.465211076, 0.320198199, 0.044519167, 0.177839798, 0.261145003, -0.143275875, 0.00, 'Services', 1],
    [472, -3.043540624, -3.157307121, 1.08846278, 2.288643618, 1.35980513, -1.064822523, 0.325574266, -0.067793653, -0.270952836, -0.838586565, -0.414575448, -0.50314086, 0.676501545, -1.692028933, 2.000634839, 0.666780354, 0.599717413, 1.725321008, 0.283345193, 2.102338792, 0.661695925, 0.435477209, 1.375965742, -0.293803153, 0.279798033, -0.145361715, -0.252773134, 0.035764225, 529.00, 'Shopping', 1],
    [4462, -2.303349938, 1.759247461, -0.359744747, 2.330243039, -0.821628328, -0.075787595, 0.56232014, -0.399146578, -0.238253369, -1.52541202, 2.032912163, -6.560124238, 0.022937328, -1.470101566, -0.698826431, -2.282193823, -4.781830912, -2.615664918, -1.33444108, 0.416737233, -0.294166319, -0.932391215, 0.172726303, -0.087330023, -0.156114263, -0.54262823, 0.039565985, -0.153029412, 239.93, 'Travel', 1],
    [6986, -4.397974441, 1.35836703, -2.592844195, 2.679786965, -1.128131343, -1.706536323, -3.496197173, -0.24877764, -0.247767931, -4.801637406, 4.895839313, -10.91281902, 0.184371556, -6.771097232, -0.007321588, -7.358083099, -12.59841854, -5.131548599, 0.308333939, -0.17160791, 0.573573937, 0.17696773, -0.436206884, -0.05350192, 0.252405265, -0.657487823, -0.827136015, 0.849573379, 59.00, 'Groceries', 1],
    [8408, -4.13283733, 5.181314815, -6.113898032, 5.869904212, -3.243557022, -1.810303357, -3.103934968, 1.442340156, -3.424422247, -5.20163158, 4.41235336, -5.889547522, 1.09249713, -6.643886259, 0.69752932, -4.10266408, -5.539129548, -4.331532135, 0.21830006, 0.496863339, 0.584611442, -0.213233215, -0.08353934, 0.08447817, 0.224345228, 0.03770487, 0.463230559, 0.18357908, 1.00, 'Utilities', 1]
]

# THIS IS THE FUNCTION THAT WAS ACCIDENTALLY DELETED. IT IS NOW RESTORED.
def generate_random_v_features():
    """Generates a list of 28 random float values simulating the V features."""
    return [random.uniform(-3, 3) for _ in range(28)]

def generate_normal_transaction():
    """Generates a single row for a normal transaction."""
    features = generate_random_v_features()
    amount = round(random.choices(
        population=[random.uniform(1, 50), random.uniform(51, 150), random.uniform(151, 500)],
        weights=[0.85, 0.1, 0.05],
        k=1
    )[0], 2)
    time_step = random.randint(1, 172000)
    category = random.choice(CATEGORIES)
    return [time_step] + features + [amount, category, 0]  # 0 for normal

def main():
    """Main function to generate the data and write to a CSV file."""
    all_transactions = []

    print(f"Generating {NUM_NORMAL_TRANSACTIONS} normal transactions...")
    for _ in range(NUM_NORMAL_TRANSACTIONS):
        all_transactions.append(generate_normal_transaction())

    print(f"Adding {len(REAL_ANOMALIES)} real anomalies...")
    all_transactions.extend(REAL_ANOMALIES)

    print("Shuffling transactions...")
    random.shuffle(all_transactions)

    print(f"Writing {len(all_transactions)} total transactions to '{OUTPUT_FILE}'...")
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(all_transactions)
    
    print("\nDone! Your guaranteed-to-work test CSV file is ready.")

if __name__ == '__main__':
    main()