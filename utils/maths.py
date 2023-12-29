class int_roman:
    tallies = {
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000,
    }

    def roman_to_int(self, romanNumeral):
        sum = 0
        for i in range(len(romanNumeral) - 1):
            left = romanNumeral[i]
            right = romanNumeral[i + 1]
            if self.tallies[left] < self.tallies[right]:
                sum -= self.tallies[left]
            else:
                sum += self.tallies[left]
        sum += self.tallies[romanNumeral[-1]]
        return sum

    def int_to_Roman(self, num):
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
        roman_num = ""
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syb[i]
                num -= val[i]
            i += 1
        return roman_num
