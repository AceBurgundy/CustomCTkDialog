from CustomCTkDialog import Dialog, folder_picker, file_picker, AlertType

def main():
    # test prompt
    try:
        name = Dialog.prompt("Enter your name:", default_text="Alice")
        print("Prompt returned:", name)
    except ValueError as error:
        print("Prompt canceled:", error)

    # test confirm
    confirmed = Dialog.confirm("Do you want to continue?")
    print("Confirm returned:", confirmed)

    # test alert
    Dialog.alert(AlertType.SUCCESS, "Test Alert", "This is a success alert!")

    # test file picker (if EXE exists locally)
    directories = file_picker(initialdir="D:/")
    print("Selected files:", directories)

    # test directory picker (if EXE exists locally)
    directories = folder_picker(initialdir="D:/")
    print("Selected folders:", directories)

if __name__ == "__main__":
    main()
