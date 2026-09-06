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


# def booth_pp_row(x: int, y_booth: int, nx_jm1: int = 0):
#     zero_pre = booth_pre_enc_gate(y_booth)
#     neg_i, ot_i, cor_i = booth_enc_tr(y_booth, zero_pre)
#     nx_jm1o = compact_decoder(neg_i, nx_jm1)


#     # Initialize output lists for 8 bits
#     nx_j = [0] * 9
#     pp_ij = [0] * 9

#     # Extract individual bits of x using bit shifts: (x >> bit_position) & 1
#     x0 = (x >> 0) & 1
#     x1 = (x >> 1) & 1
#     x2 = (x >> 2) & 1
#     x3 = (x >> 3) & 1
#     x4 = (x >> 4) & 1
#     x5 = (x >> 5) & 1
#     x6 = (x >> 6) & 1
#     x7 = (x >> 7) & 1

#     # First bit cell (uses initial nx_jm1)
#     nx_j[0], pp_ij[0] = decoder_tr(nx_jm1o, x0, neg_i, zero_pre, ot_i)

#     # Subsequent bit cells (pass nx_j from previous bit)
#     nx_j[1], pp_ij[1] = decoder_tr(nx_j[0], x1, neg_i, zero_pre, ot_i)
#     nx_j[2], pp_ij[2] = decoder_tr(nx_j[1], x2, neg_i, zero_pre, ot_i)
#     nx_j[3], pp_ij[3] = decoder_tr(nx_j[2], x3, neg_i, zero_pre, ot_i)
#     nx_j[4], pp_ij[4] = decoder_tr(nx_j[3], x4, neg_i, zero_pre, ot_i)
#     nx_j[5], pp_ij[5] = decoder_tr(nx_j[4], x5, neg_i, zero_pre, ot_i)
#     nx_j[6], pp_ij[6] = decoder_tr(nx_j[5], x6, neg_i, zero_pre, ot_i)
#     nx_j[7], pp_ij[7] = decoder_tr(nx_j[6], x7, neg_i, zero_pre, ot_i)
#     nx_j[8], pp_ij[8] = decoder_tr(nx_j[7], x7, neg_i, zero_pre, ot_i)

#     return pp_ij, cor_i
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

    return pp, nx, cor_i


a, b, c = booth_pp_row(0b00000010, 0b011, 0b0)

print(a)
print(b)
print(c)

print(f"pp = {a:09b}")
print(f"nx = {b:09b}")
print(f"cor = {c:09b}")
