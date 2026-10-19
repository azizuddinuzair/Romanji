def line_by_line(file1, file2):
    with open(file1, "r") as f:
        list1 = [line.rstrip("\n") for line in f]

    with open(file2, "r") as f:
        list2 = [line.rstrip("\n") for line in f]

    spacing = 75
    total_lines = max(len(list1), len(list2))

    for i in range(total_lines):
        line1 = list1[i] if i < len(list1) else ""
        line2 = list2[i] if i < len(list2) else ""
        
        parts1 = [
            line1[k : k + spacing] for k in range(0, len(line1), spacing)
        ] or [""]
        
        parts2 = [
            line2[k : k + spacing] for k in range(0, len(line2), spacing)
        ] or [""]

        sub_rows = max(len(parts1), len(parts2))
        for j in range(sub_rows):
            sub1 = parts1[j] if j < len(parts1) else ""
            sub2 = parts2[j] if j < len(parts2) else ""
            print(f"{sub1:<{spacing}} | {sub2}")


if __name__ == "__main__":
    file1 = input("Input first file: ")
    file2 = input("Input second file: ")
    line_by_line(file1, file2)