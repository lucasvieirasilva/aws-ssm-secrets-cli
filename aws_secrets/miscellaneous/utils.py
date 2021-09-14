def repeat_to_length(string_to_expand: str, length: int) -> str:
    """
        Repeat the string using a length variable

        Args:
            string_to_expand (`str`): string to repeat
            length (`int`): length

        Returns:
            `str`: generated string

        Examples:
            >>> repeat_to_length("#", 5)
            "#####"
    """
    return (string_to_expand * (int(length/len(string_to_expand))+1))[:length]
