def booth_pre_enc_gate(y_booth: int):
    if y_booth == 0 or y_booth == 7:
        zero_pre = 1
    else:
        zero_pre = 0

    return zero_pre


def booth_enc_tr(y_booth: int, zero_pre: int):
    y_2i_m1 = (y_booth >> 0) & 1
    y_2i    = (y_booth >> 1) & 1
    y_2i_p1 = (y_booth >> 2) & 1

    neg_i = y_2i_p1
    zero_i_b = 1 - zero_pre
    cor_i = neg_i & zero_i_b
    ot_i = y_2i_m1 ^ y_2i

    return neg_i, ot_i, cor_i


def compact_decoder(neg_i: int, x_j: int):
    nx_j = x_j ^ neg_i

    return nx_j


def decoder_tr(nx_jm1: int, x_j: int, neg_i: int, zero_pre: int, ot_i: int):
    nx_j = x_j ^ neg_i
    if zero_pre == 1:
        pp_ij = 0
    elif zero_pre == 0:
        if ot_i == 1:
            pp_ij = nx_j
        else:
            pp_ij = nx_jm1
            

    return nx_j, pp_ij

def booth_pp_row(x: int, y_booth: int, nx_jm1: int = 0):

    zero_pre = booth_pre_enc_gate(y_booth)
    neg_i, ot_i, cor_i = booth_enc_tr(y_booth, zero_pre)

    # Transform incoming nx_{j-1}
    nx_jm1o = compact_decoder(neg_i, nx_jm1)

    # Integer outputs
    pp = 0
    nx = 0

    # Previous nx value
    nx_prev = nx_jm1o

    # Generate 9 bits
    for j in range(9):

        # x[0] ... x[7], then sign extension x[7]
        x_bit = (x >> min(j, 7)) & 1

        nx_bit, pp_bit = decoder_tr(
            nx_prev,
            x_bit,
            neg_i,
            zero_pre,
            ot_i
        )

        # Put generated bit into integer
        nx |= (nx_bit << j)
        pp |= (pp_bit << j)

        # Feed nx_j to next decoder
        nx_prev = nx_bit
        sum = pp + cor_i

    return pp, nx, cor_i, sum


def sign_extend(value: int, from_bits: int, to_bits: int) -> int:
    value &= (1 << from_bits) - 1

    if value & (1 << (from_bits - 1)):
        value |= ((1 << (to_bits - from_bits)) - 1) << from_bits

    return value


def booth_mult(x: int, y: int):

    # ---------------------------------------------------------
    # Generate the four radix-4 Booth groups
    # ---------------------------------------------------------
    # y[-1] = 0
    #
    # row 0: {y1, y0, y-1}
    # row 1: {y3, y2, y1}
    # row 2: {y5, y4, y3}
    # row 3: {y7, y6, y5}
    # ---------------------------------------------------------

    y0 = (y >> 0) & 1
    y1 = (y >> 1) & 1
    y2 = (y >> 2) & 1
    y3 = (y >> 3) & 1
    y4 = (y >> 4) & 1
    y5 = (y >> 5) & 1
    y6 = (y >> 6) & 1
    y7 = (y >> 7) & 1

    booth0 = (y1 << 2) | (y0 << 1) | 0
    booth1 = (y3 << 2) | (y2 << 1) | y1
    booth2 = (y5 << 2) | (y4 << 1) | y3
    booth3 = (y7 << 2) | (y6 << 1) | y5

    # ---------------------------------------------------------
    # Generate partial-product rows
    # ---------------------------------------------------------

    pp0, nx0, cor0, sum0 = booth_pp_row(x, booth0, 0)
    pp1, nx1, cor1, sum1 = booth_pp_row(x, booth1, 0)
    pp2, nx2, cor2, sum2 = booth_pp_row(x, booth2, 0)
    pp3, nx3, cor3, sum3 = booth_pp_row(x, booth3, 0)

    #---------------------------------------------------------
    # Sign-extend 9-bit Booth rows to 16 bits
    #---------------------------------------------------------
    sum0 = sign_extend(sum0, 9, 16)
    sum1 = sign_extend(sum1, 9, 16)
    sum2 = sign_extend(sum2, 9, 16)
    sum3 = sign_extend(sum3, 9, 16)


    # ---------------------------------------------------------
    # Radix-4 positional shifts
    # ---------------------------------------------------------

    shifted_sum0 = sum0 << 0
    shifted_sum1 = sum1 << 2
    shifted_sum2 = sum2 << 4
    shifted_sum3 = sum3 << 6

    # print(f"Shifted sums: {shifted_sum0:016b} ({shifted_sum0}), {shifted_sum1:016b} ({shifted_sum1}), {shifted_sum2:016b} ({shifted_sum2}), {shifted_sum3:016b} ({shifted_sum3})")

    # ---------------------------------------------------------
    # Final product
    # ---------------------------------------------------------

    product = (
        shifted_sum0
        + shifted_sum1
        + shifted_sum2
        + shifted_sum3
    )

    # return product
    # return sign_extend(product, 16, 16), sum0, sum1, sum2, sum3
    return sign_extend(product, 16, 16), shifted_sum0, shifted_sum1, shifted_sum2, shifted_sum3


# def twos_complement_to_int(binary_str: str) -> int:
#     """
#     Converts an N-bit Two's Complement binary string back into a signed integer.
#     """
#     bits = len(binary_str)
#     val = int(binary_str, 2)
    
#     # If the Most Significant Bit (MSB) is 1, the number is negative
#     if (val & (1 << (bits - 1))) != 0:
#         val = val - (1 << bits)
        
#     return val

# x = 0b00010110  # 22 in decimal
# y = 0b11111101  # 5 in decimal
# result = booth_mult(x, y)

# print(f"X: {x:08b} ({x}), Y: {y:08b} ({y}), Result: {result:015b} ({result})")
# print(f"X: {twos_complement_to_int(f'{x:08b}')}, Y: {twos_complement_to_int(f'{y:08b}')}, Result as signed integer: {twos_complement_to_int(f'{result:015b}')}")


# import numpy as np

# N = 100_000

# for _ in range(N):

#     # X: uniform integer in [-127, 127]
#     x = np.random.randint(-127, 128)
#     y = int(np.clip(
#         np.rint(np.random.normal(-1.64, 24.69)),
#         -128,
#         127
#     ))

#     # Feed directly to multiplier
#     result = booth_mult(x, y)

#     print(f"x={x}, y={y}, Result as signed integer: {twos_complement_to_int(f'{result:015b}')}")

import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# Two's complement conversion
# ============================================================

def twos_complement_to_int(binary_str: str) -> int:
    """
    Converts an N-bit Two's Complement binary string
    back into a signed integer.
    """
    bits = len(binary_str)
    val = int(binary_str, 2)

    # If MSB is 1, number is negative
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)

    return val


# ============================================================
# Generate operands
# ============================================================

N = 100_000

rng = np.random.default_rng(42)

# X: integer uniformly distributed between -127 and 127
x_values = rng.integers(-127, 128, size=N)

# Y: Gaussian distribution
y_values = np.rint(
    rng.normal(
        loc=-1.64,
        scale=24.69,
        size=N
    )
).astype(int)

# Keep Y within signed 8-bit range
y_values = np.clip(y_values, -128, 127)


# ============================================================
# Run multiplier
# ============================================================

results = np.empty(N, dtype=np.int64)

shifted_sum_0_values = np.empty(N, dtype=np.int64)
shifted_sum_1_values = np.empty(N, dtype=np.int64)
shifted_sum_2_values = np.empty(N, dtype=np.int64)
shifted_sum_3_values = np.empty(N, dtype=np.int64)

row3_percentage = np.empty(N, dtype=np.float64)
row3_magnitude_percentage = np.empty(N, dtype=np.float64)

for i in range(N):

    x = int(x_values[i])
    y = int(y_values[i])

    # result = booth_mult(x, y)
    result, shifted_sum_0, shifted_sum_1, shifted_sum_2, shifted_sum_3 = booth_mult(x, y)

    # Convert 16-bit multiplier output to binary string
    result_binary = format(result & 0xFFFF, '016b')
    shifted_sum_0_binary = format(shifted_sum_0 & 0xFFFF, '016b')
    shifted_sum_1_binary = format(shifted_sum_1 & 0xFFFF, '016b')
    shifted_sum_2_binary = format(shifted_sum_2 & 0xFFFF, '016b')
    shifted_sum_3_binary = format(shifted_sum_3 & 0xFFFF, '016b')

    # Convert two's-complement binary to signed integer
    results[i] = twos_complement_to_int(result_binary)
    shifted_sum_0_values[i] = twos_complement_to_int(shifted_sum_0_binary)
    shifted_sum_1_values[i] = twos_complement_to_int(shifted_sum_1_binary)
    shifted_sum_2_values[i] = twos_complement_to_int(shifted_sum_2_binary)
    shifted_sum_3_values[i] = twos_complement_to_int(shifted_sum_3_binary)

    # ========================================================
    # Contribution of the LAST Booth row
    # ========================================================

    if results[i] != 0:
        # Signed contribution
        row3_percentage[i] = (
            shifted_sum_3_values[i] / results[i]
        ) * 100

        # Magnitude contribution
        row3_magnitude_percentage[i] = (
            abs(shifted_sum_3_values[i]) / abs(results[i])
        ) * 100
    else:
        row3_percentage[i] = 0
        row3_magnitude_percentage[i] = 0


# ============================================================
# Gaussian function
# ============================================================

def gaussian(x, mu, sigma):

    return (
        1.0 / (sigma * np.sqrt(2 * np.pi))
        * np.exp(
            -0.5 * ((x - mu) / sigma) ** 2
        )
    )


# ============================================================
# Fit Gaussian models
# ============================================================

x_mu = np.mean(x_values)
x_sigma = np.std(x_values, ddof=1)

y_mu = np.mean(y_values)
y_sigma = np.std(y_values, ddof=1)

result_mu = np.mean(results)
result_sigma = np.std(results, ddof=1)


# ============================================================
# Triple plot
# ============================================================

fig, axes = plt.subplots(
    1, 3,
    figsize=(18, 5)
)


# ============================================================
# Plot 1: X
# ============================================================

axes[0].hist(
    x_values,
    bins=np.arange(-127.5, 128.5, 1),
    density=True,
    alpha=0.7
)

xx = np.linspace(
    x_values.min(),
    x_values.max(),
    1000
)

axes[0].plot(
    xx,
    gaussian(xx, x_mu, x_sigma),
    linewidth=2,
    label=(
        f"Gaussian fit\n"
        f"$\\mu$ = {x_mu:.2f}\n"
        f"$\\sigma$ = {x_sigma:.2f}"
    )
)

axes[0].set_title("X Distribution")
axes[0].set_xlabel("X")
axes[0].set_ylabel("Probability Density")
axes[0].legend()
axes[0].grid(alpha=0.25)


# ============================================================
# Plot 2: Y
# ============================================================

axes[1].hist(
    y_values,
    bins=np.arange(
        y_values.min() - 0.5,
        y_values.max() + 1.5,
        1
    ),
    density=True,
    alpha=0.7
)

yy = np.linspace(
    y_values.min(),
    y_values.max(),
    1000
)

axes[1].plot(
    yy,
    gaussian(yy, y_mu, y_sigma),
    linewidth=2,
    label=(
        f"Gaussian fit\n"
        f"$\\mu$ = {y_mu:.2f}\n"
        f"$\\sigma$ = {y_sigma:.2f}"
    )
)

axes[1].set_title("Y Distribution")
axes[1].set_xlabel("Y")
axes[1].set_ylabel("Probability Density")
axes[1].legend()
axes[1].grid(alpha=0.25)


# ============================================================
# Plot 3: Multiplier result
# ============================================================

axes[2].hist(
    results,
    bins=100,
    density=True,
    alpha=0.7
)

rr = np.linspace(
    results.min(),
    results.max(),
    1000
)

axes[2].plot(
    rr,
    gaussian(rr, result_mu, result_sigma),
    linewidth=2,
    label=(
        f"Gaussian fit\n"
        f"$\\mu$ = {result_mu:.2f}\n"
        f"$\\sigma$ = {result_sigma:.2f}"
    )
)

axes[2].set_title("Multiplier Result Distribution")
axes[2].set_xlabel("Result")
axes[2].set_ylabel("Probability Density")
axes[2].legend()
axes[2].grid(alpha=0.25)


plt.tight_layout()
plt.show()


# ============================================================
# Partial Product Distributions — ALL SIMULTANEOUSLY
# ============================================================

pp_data = [
    (shifted_sum_0_values, "Row 0", 0),
    (shifted_sum_1_values, "Row 1", 2),
    (shifted_sum_2_values, "Row 2", 4),
    (shifted_sum_3_values, "Row 3", 6)
]

fig, axes = plt.subplots(
    2, 2,
    figsize=(16, 11)
)

for ax, (data, name, shift) in zip(axes.ravel(), pp_data):

    mu = np.mean(data)
    sigma = np.std(data, ddof=1)

    data_min = int(np.min(data))
    data_max = int(np.max(data))

    # Histogram
    ax.hist(
        data,
        bins=100,
        alpha=0.75,
        edgecolor='black'
    )

    # Gaussian fit
    xx = np.linspace(data_min, data_max, 1000)

    gaussian_counts = (
        gaussian(xx, mu, sigma)
        * len(data)
        * (data_max - data_min) / 100
    )

    ax.plot(
        xx,
        gaussian_counts,
        linewidth=2,
        label=(
            f"Gaussian fit\n"
            f"$\\mu$ = {mu:.2f}\n"
            f"$\\sigma$ = {sigma:.2f}"
        )
    )

    ax.set_title(
        f"{name} Partial Product\n"
        f"Shift = {shift} bits",
        fontsize=15
    )

    ax.set_xlabel("Value", fontsize=12)
    ax.set_ylabel("Number of Samples", fontsize=12)

    ax.set_xlim(data_min, data_max)

    ax.legend()
    ax.grid(alpha=0.25)

plt.suptitle(
    "Radix-4 Booth Partial-Product Distributions",
    fontsize=18
)

plt.tight_layout()
plt.show()

# ============================================================
# Statistics
# ============================================================

print("=" * 60)

print("X:")
print(f"  Mean = {x_mu:.4f}")
print(f"  Std  = {x_sigma:.4f}")
print(f"  Min  = {x_values.min()}")
print(f"  Max  = {x_values.max()}")

print()

print("Y:")
print(f"  Target Mean = -1.64")
print(f"  Target Std  = 24.69")
print(f"  Actual Mean = {y_mu:.4f}")
print(f"  Actual Std  = {y_sigma:.4f}")
print(f"  Min         = {y_values.min()}")
print(f"  Max         = {y_values.max()}")

print()

print("Multiplier Result:")
print(f"  Mean = {result_mu:.4f}")
print(f"  Std  = {result_sigma:.4f}")
print(f"  Min  = {results.min()}")
print(f"  Max  = {results.max()}")

print("=" * 60)


print()
print("Shifted Sum Statistics:")
print("=" * 60)

for name, data in [
    ("Shifted Sum 0", shifted_sum_0_values),
    ("Shifted Sum 1", shifted_sum_1_values),
    ("Shifted Sum 2", shifted_sum_2_values),
    ("Shifted Sum 3", shifted_sum_3_values)
]:
    print(
        f"{name}: "
        f"Mean = {np.mean(data):.4f}, "
        f"Std = {np.std(data, ddof=1):.4f}, "
        f"Min = {np.min(data)}, "
        f"Max = {np.max(data)}"
    )



# -----------------------------------------------------------------------------------
print()
print("=" * 60)
print("LAST ROW (ROW 3) CONTRIBUTION")
print("=" * 60)

print(
    f"Mean signed contribution     = "
    f"{np.mean(row3_percentage):.2f}%"
)

print(
    f"Mean magnitude contribution  = "
    f"{np.mean(row3_magnitude_percentage):.2f}%"
)

print(
    f"Median magnitude contribution = "
    f"{np.median(row3_magnitude_percentage):.2f}%"
)

print(
    f"Maximum magnitude contribution = "
    f"{np.max(row3_magnitude_percentage):.2f}%"
)

print("=" * 60)

plt.figure(figsize=(12, 7))

plt.hist(
    row3_magnitude_percentage,
    bins=100,
    alpha=0.75,
    edgecolor='black'
)

plt.xlabel(
    "Last Row Contribution (%)",
    fontsize=13
)

plt.ylabel(
    "Number of Samples",
    fontsize=13
)

plt.title(
    "Contribution of Last Booth Row to Final Result",
    fontsize=16
)

plt.grid(alpha=0.25)
plt.tight_layout()
plt.show()