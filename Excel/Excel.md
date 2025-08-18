The video provides a comprehensive guide to data analysis in Excel, covering everything from basic data manipulation to advanced dashboard creation. Below are comprehensive notes on the important formulas, their usage, problem statements, and key insights related to PivotTables, excluding the Power Query section as requested. I have also separated out the various tips and tricks shared by the author.

---

### Excel Fundamentals and Data Manipulation

The video begins by introducing Microsoft Excel as a versatile and important software for data analysis, tracking information, updating projects, and collaboration. It highlights the basic layout of an Excel file, including the ribbon, grid area (rows and columns intersecting to form cells), and status bar.

The sample dataset used for initial demonstrations is an employee dataset containing details like Employee IDs, Names, Gender, Department, Salaries, Start Date, FTE (Full-Time Equivalent), Employee Type, and Work Location.

#### Key Data Manipulation Concepts and Techniques:

- **Selecting Data**:
    - To select an entire column: **`Ctrl + Shift + Down Arrow`**.
    - To select an entire row: **`Ctrl + Shift + Right Arrow`**.
    - To select an entire grid of data: **`Ctrl + A`** or **`Ctrl + Shift + 8`**.
- **Filtering Data**:
    - **Application**: Select data (e.g., using `Ctrl + A`), then go to the `Home` ribbon, select `Sort & Filter`, and click `Filter`.
    - **Single/Multiple Item Filtering**: Click the filter arrow in a column header to select single or multiple items from a dropdown list (e.g., selecting employees from 'Chennai' office).
    - **Multiple Column Filtering**: Apply filters on multiple columns simultaneously (e.g., 'multiple locations' and 'female employees') to get a subset of data.
    - **Special Filters for Numbers/Dates**:
        - **Number Filters**: For columns like 'Salary', use `Number Filters` (e.g., 'Greater Than', 'Top 10', 'Bottom 10').
        - **Date Filters**: For columns like 'Start Date', use `Date Filters` (e.g., 'Last Week', 'Last Month', 'Between').
    - **Right-Click Filtering**: Right-click on a specific cell value you want to filter by, then select `Filter` > `Filter by Selected Cell's Value`. This is a quick way to filter for that exact value.
    - **Clearing Filters**:
        - Manually: Go to individual columns and clear them (can be tedious).
        - Globally: Go to `Home` ribbon > `Sort & Filter` > `Clear`.
- **Sorting Data**:
    - **Single Column Sort**: Select the column, then `Home` ribbon > `Sort & Filter` > `Smallest to Largest` or `Largest to Smallest`.
    - **Multi-Level Sorting (Puzzle)**: The video poses a puzzle: how to sort employees by gender first, and then by salary within each gender group. (This implies using custom sort options, though not explicitly detailed as a solution in this segment).
- **Identifying Duplicates with Conditional Formatting**:
    - **Purpose**: Spot duplicate information, especially useful for identifying data quality issues (e.g., same employee ID with different names).
    - **Method**: Select the column (e.g., 'Employee ID'), go to `Home` ribbon > `Conditional Formatting` > `Highlight Cell Rules` > `Duplicate Values`. Duplicates will be highlighted.
    - **Filtering by Color**: Once highlighted, you can use the filter option and select `Filter by Color` to view only the duplicate entries.
    - **Clearing Conditional Formatting**: Select the data, `Home` ribbon > `Conditional Formatting` > `Clear Rules` > `Clear Rules from Selected Cells` or `Clear Rules from Entire Worksheet`.
- **Quick Data Summaries (AutoSum)**:
    - **Total/Sum**: Select an entire column (e.g., 'Salary' or 'FTE'), then go to `Home` ribbon > `AutoSum` button, or use the shortcut **`Alt + =`**. Excel automatically inserts a `SUM` formula at the bottom of the selected column.
    - **Counts for Text Values**: While `AutoSum` works for numbers, it won't directly sum text values. You'll need specific functions like `COUNTA` for that.

### Essential Excel Formulas and Functions

The video transitions to explaining essential Excel formulas using the extended HR dataset, now structured as an Excel Table named "staff".

#### Problem 1: Total Salary and Head Count by Department

- **Goal**: To determine how many people work in each department and the total salary paid per department for an HR meeting.
- **Setup**: Create a new sheet, copy all department names from the 'staff' table, and then use `Data` ribbon > `Remove Duplicates` to get a unique list of departments.
- **Formulas Used**:
    - **`COUNTIFS`**: Used to count the number of employees in each department.
        - **Usage**: `=COUNTIFS(staff[Department], B3)` where `staff[Department]` is the range to check, and `B3` is the specific department name (e.g., "Training").
        - **Pro Trick (Excel 365 Spilling)**: Instead of pointing to a single cell (`B3`), you can point to an entire range of unique departments (`B3#`). This automatically "spills" the results for all departments without dragging the formula down.
    - **`SUMIFS`**: Used to calculate the total salary for each department.
        - **Usage**: `=SUMIFS(staff[Salary], staff[Department], B3#)` where `staff[Salary]` is the range to sum, `staff[Department]` is the criteria range, and `B3#` is the department criteria (spilling for all departments).
    - **`AVERAGEIFS`**: Used to calculate the average salary for each department.
        - **Usage**: `=AVERAGEIFS(staff[Salary], staff[Department], B6#)`.
- **Challenge**: Calculate the "permanent head count" for each department, counting only permanent staff.

#### Problem 2: All Employees with More Than 100,000 Salary

- **Goal**: To extract a list of employees earning over a specified salary.
- **Manual Method**: Apply filters (`Ctrl + Shift + L`), then use `Number Filters` > `Greater Than` on the 'Salary' column.
- **Formula Method (Excel 365)**:
    - **`FILTER`**: Extracts a subset of data that meets specific criteria.
        - **Usage**: `=FILTER(staff, staff[Salary]>100000)` This returns the entire row for employees meeting the condition as a "spilled range".
        - **Nuance**: `FILTER` function returns raw data; it does not automatically apply formatting (e.g., dates may appear as numbers).
        - **Pro Trick**: Pre-select the range where the filtered data will spill and apply desired formatting (e.g., Date, Currency) beforehand.
        - **Getting Headers**: To include headers with the filtered data, use `=staff[#Headers]`.
    - **Extracting Specific Columns with `CHOOSECOLS` (Excel 365)**:
        - **Goal**: To see only a subset of columns (e.g., Employee ID, Names, Department, Salary) from the filtered data.
        - **`CHOOSECOLS`**: Selects specific columns from an array or range.
        - **Usage (Nesting)**: `=CHOOSECOLS(FILTER(staff, staff[Salary]>F67), 1, 2, 3, 5, 6)`. Here, the `FILTER` output is nested inside `CHOOSECOLS`.
        - **Dynamic Input**: The salary threshold can be linked to a cell (e.g., `F67`) for dynamic adjustments.
        - **Applying to Headers**: Use `CHOOSECOLS(staff[#Headers], 1, 2, 3, 5, 6)` to get specific headers.

#### Problem 3: All Female Employees with More Than 100,000 Salary

- **Goal**: To filter data based on multiple conditions.
- **Multiple Conditions in `FILTER`**:
    - **Syntax**: Conditions are enclosed in brackets and multiplied together using `*`.
    - **Usage**: `=FILTER(staff, (staff[Salary]>F67) * (staff[Gender]="Female"))`.
    - **Pro Trick (Continuous Column Selection)**: Instead of listing column numbers in `CHOOSECOLS`, for a continuous range of columns (e.g., from 'Employee ID' to 'Salary'), you can use `staff[[Employee ID]:[Salary]]` as the first argument in `FILTER`. This is a more elegant syntax.
- **Challenge**: Add a third condition: employees must have joined in 2020 or after.

#### Problem 4: Lowest, Highest, and Top Five Salary Values

- **Goal**: To find extreme values and a list of top N values.
- **Formulas Used**:
    - **`MIN`**: Returns the lowest value in a range.
        - **Usage**: `=MIN(staff[Salary])`.
    - **`MAX`**: Returns the highest value in a range.
        - **Usage**: `=MAX(staff[Salary])`.
    - **`LARGE`**: Returns the K-th largest value in a dataset.
        - **Usage**: `=LARGE(staff[Salary], K)` where `K` is 1 for the highest, 2 for the second highest, etc..
        - **Pro Trick**: List the `K` values (1, 2, 3, 4, 5) in a separate column/range and reference them, then drag the `LARGE` formula down. This helper column can be hidden.
    - **Alternative for Top N (Excel 365)**:
        - **`SORT`**: Sorts a range or array.
            - **Usage**: `=SORT(staff[Salary], , -1)` to sort salaries in descending order (`-1` indicates descending).
        - **`TAKE`**: Returns a specified number of rows or columns from the start or end of an array.
            - **Usage**: `=TAKE(SORT(staff[Salary], , -1), 5)` This takes the top 5 values after sorting.
            - **Dynamic Input**: The number of values to take (e.g., 5) can be linked to a cell for dynamic adjustment.
- **For Specific Groups (e.g., Male/Female Employees)**:
    - **`MINIFS`**: Returns the minimum value that satisfies specific criteria (available from Excel 2016/2019).
        - **Usage**: `=MINIFS(staff[Salary], staff[Gender], D3)`.
        - **Pro Trick**: Use `F4` key to apply absolute referencing (`D$3`) when dragging formulas.
    - **`MAXIFS`**: Returns the maximum value that satisfies specific criteria.
        - **Usage**: `=MAXIFS(staff[Salary], staff[Gender], D3)`.
    - **Top N for Groups**: Combine `FILTER` (to narrow down to the group) with `LARGE` or `SORT` and `TAKE` (to get the top N).

#### Problem 5: List All Departments and Count Them

- **Goal**: Get a unique list of departments and count how many there are.
- **Formula Used**:
    - **`UNIQUE` (Excel 365)**: Returns a list of unique values from a range.
        - **Usage**: `=UNIQUE(staff[Department])`.
        - **Nuance**: Lists departments in the order they first appear in the data.
        - **Pro Trick**: Combine with `SORT` for alphabetical order: `=SORT(UNIQUE(staff[Department]))`.
    - **`COUNTA`**: Counts the number of non-empty cells.
        - **Usage with Spill Operator (`#`)**: `=COUNTA(B4#)` where `B4#` refers to the entire spilled range of unique departments. This makes the count dynamic; it updates if more unique departments appear.
- **Challenge**: Display all departments in a single cell, comma-separated.

#### Problem 6: Looking Up Specific Information (VLOOKUP, INDEX MATCH, XLOOKUP)

- **Goal**: Retrieve employee information based on a lookup value (e.g., Employee ID or Last Name).
- **Manual Method**: Use filters on the data to find a specific row.
- **`VLOOKUP`**: Looks for a value in the _first_ column of a table and returns a corresponding value from a specified column in the same row.
    - **Usage**: `=VLOOKUP(C4, staff, 2, FALSE)` where `C4` is the lookup value, `staff` is the table array, `2` is the column index for the 'First Name', and `FALSE` ensures an exact match.
    - **Pro Trick**: Instead of hardcoding column numbers (2, 3, 5, 6), place them in a helper row/column and reference those cells. Make the lookup value reference absolute (`$C$4`) to drag the formula.
    - **Handling Errors (`#N/A`)**:
        - **`IFERROR`**: Returns a specified value if a formula results in an error.
        - **Usage**: `=IFERROR(VLOOKUP(...), "Not Found")`.
    - **Limitation**: `VLOOKUP` can only look up values in the leftmost column of the specified table array. It also returns only the _first_ match if duplicates exist.
- **`INDEX MATCH` (for older Excel versions to overcome `VLOOKUP`'s limitation)**:
    - **Goal**: Look up based on a column that isn't the first (e.g., 'Last Name').
    - **`MATCH`**: Finds the relative position of an item in a range.
        - **Usage**: `=MATCH("Scad", staff[Last Name], 0)` returns the row number where "Scad" is found (0 for exact match).
    - **`INDEX`**: Returns a value from a specified row and column within a range.
        - **Usage**: `=INDEX(staff[Employee ID], 43)` returns the employee ID from the 43rd row.
    - **Combined Usage**: `=INDEX(staff[Employee ID], MATCH("Scad", staff[Last Name], 0))`.
    - **Limitation**: Similar to `VLOOKUP`, `INDEX MATCH` also returns only the _first_ match for duplicates.
- **`XLOOKUP` (Excel 365 - modern and improved lookup)**:
    - **Purpose**: A versatile function that can do everything `VLOOKUP`, `HLOOKUP`, and `INDEX MATCH` can, and more.
    - **Basic Usage**: `=XLOOKUP(C4, staff[Employee ID], staff[First Name])` where `C4` is lookup value, `staff[Employee ID]` is the lookup array, and `staff[First Name]` is the return array. It defaults to exact match.
    - **Advantage 1: Built-in Error Handling**: Includes an optional `if_not_found` argument.
        - **Usage**: `=XLOOKUP(..., "Not Found")`.
    - **Advantage 2: Any Column Lookup**: `XLOOKUP` is not restricted to the first column; you define separate lookup and return arrays.
    - **Advantage 3: Return Multiple Values/Entire Row**:
        - **Usage**: `=XLOOKUP("Tawell", staff[Last Name], staff)` returns the entire row from the 'staff' table for "Tawell".
        - **`TRANSPOSE`**: To change the orientation (rows to columns) of the returned data, nest `XLOOKUP` inside `TRANSPOSE`.
            - **Usage**: `=TRANSPOSE(XLOOKUP("Tawell", staff[Last Name], staff))`.
- **Challenge**: Find _all_ employees with a specific salary (e.g., $120,000), not just the first one. (Hint: Revisit `FILTER`).

#### Problem 7: Highest Salaried Person (and handling ties)

- **Goal**: Find the name of the person with the highest salary, and if there are ties, list all of them.
- **Single Highest (using `XLOOKUP` and `MAX`)**:
    - **Usage**: `=XLOOKUP(MAX(staff[Salary]), staff[Salary], staff[First Name] & " " & staff[Last Name])`.
    - **Pro Trick**: Concatenate 'First Name' and 'Last Name' directly within the `return_array` argument of `XLOOKUP` using the `&` operator.
- **Listing All Tied Highest (using `FILTER` and `TEXTJOIN`)**:
    - **`FILTER`**: Filter the staff table where salary equals the maximum salary.
        - **Usage**: `=FILTER(staff[First Name] & " " & staff[Last Name], staff[Salary]=MAX(staff[Salary]))`.
    - **`TEXTJOIN`**: Combines text from multiple ranges with a specified delimiter.
        - **Usage**: `=TEXTJOIN(", ", , FILTER(...))` to list all names comma-separated in a single cell.

#### Problem 8: All Employees Who Joined in the Month of March

- **Goal**: Filter employees by the month of their start date, irrespective of the year.
- **`FILTER` with Date Functions**:
    - **`MONTH`**: Extracts the month number from a date.
    - **Usage**: `=FILTER(staff[[Employee ID]:[Last Name]], MONTH(staff[Start Date])=3)`.
    - **General Filtering on Text Parts**: The video also shows a general trick of using functions like `LEFT` within `FILTER` to check text conditions (e.g., `LEFT(Staff[First Name],1)="H"`).
- **Challenge**: Get all female employees who started on a Monday.

#### Problem 9: Department Report

- **Goal**: Create a concise report showing department headcounts, average salaries, percentage difference from overall average, and highest salary per department.
- **Overall Metrics**:
    - **Overall Headcount**: `=COUNTA(staff[Employee ID])`.
    - **Overall Average Salary**: `=AVERAGE(staff[Salary])`.
    - **Overall Highest Salary**: `=MAX(staff[Salary])`.
- **Department-Level Metrics**:
    - **Department List (Sorted)**: `=SORT(UNIQUE(staff[Department]))`.
    - **Headcounts**: `=COUNTIFS(staff[Department], B6#)`.
    - **Average Salaries**: `=AVERAGEIFS(staff[Salary], staff[Department], B6#)`.
    - **Percentage Difference from Overall Average**: `D6# - D3` where `D6#` is the spilled range of department averages and `D3` is the overall average. Excel's spilling handles the reference correctly.
- **Visualisation (Conditional Formatting)**:
    - **Data Bars**: `Home` ribbon > `Conditional Formatting` > `Data Bars` to visually represent values (e.g., salary differences).
    - **Pro Tip (Data Bar Customisation)**: To show both bars and numbers clearly, customize the data bar rule (Manage Rules) to "Show Bar Only". Then, in an adjacent column, use a simple formula (`=E6#`) to display the numbers themselves, formatted separately.
- **Challenge**: Calculate the median salary and female ratio in each department.

### Pivot Table Nuances and Tricks

The video transitions to Pivot Tables, using a made-up call centre dataset.

- **Data Preparation for Pivot Tables**:
    - **Convert to Table**: Select any cell in your data, then press **`Ctrl + T`** to convert it into an Excel Table. This applies consistent formatting and enables the `Table Design` ribbon.
    - **Name the Table**: Give the table a descriptive name (e.g., "calls") from the `Table Design` ribbon.
- **Creating a Pivot Table**:
    - From `Table Design` ribbon: `Summarize with PivotTable`.
    - From `Insert` ribbon: `PivotTable`.
    - **Recommendation**: `Recommended Pivots` (Excel 2016/365) can suggest common pivot reports.
    - **Location**: Typically in a `New Worksheet`, but can be placed in an `Existing Worksheet`.
- **Pivot Table Field Areas**:
    - **Fields List**: Shows all columns from your source data.
    - **Rows Area**: Fields dragged here appear as rows in the report.
    - **Columns Area**: Fields dragged here appear as columns in the report.
    - **Values Area**: Fields dragged here are summarized (counted, summed, averaged). Excel tries to guess the summarisation method.
    - **Filters Area**: Fields dragged here create report-level filters.
- **Customising Pivot Table Calculations**:
    - **Changing Summarisation**: Right-click on a number in the Pivot Table > `Summarize Values By` > Select `Sum`, `Count`, `Average`, `Max`, `Min`, etc..
    - **Formatting Values**: Right-click on a number > `Number Format` to apply specific number, currency, or decimal point formatting.
    - **Showing Values As**: Right-click on a number > `Show Values As` > Options like `Running Total In`, `Percentage of Row Total`, `Percentage of Column Total`, etc..
- **Filtering and Sorting in Pivot Tables**:
    - **Top N Filtering**: Click the filter button next to a row/column label in the pivot table > `Value Filters` > `Top 10` (or `Greater Than`, etc.).
    - **Sorting Data in Pivot**: Right-click on the data values in the pivot table > `Sort` > `Largest to Smallest` or `Smallest to Largest`. This ensures the report remains sorted even when data or filters change.
    - **Manual Reordering of Rows/Columns**: Click on the edge of a row or column label (e.g., a department name or a duration bucket) in the pivot table and drag it to manually rearrange the order. This overrides alphabetical or numerical sorting and is useful for logical ordering (e.g., 'Under 10 mins', '10-30 mins').
- **Grouping Data in Pivot Tables**:
    - **Automatic Date Grouping**: When a date field is added to rows, Excel automatically groups it (e.g., by Month, Quarter, Year). You can expand/collapse these groups using the `+`/`-` buttons.
    - **Manual Numerical/Date Grouping**: Right-click on a number or date field in the pivot table > `Group`. You can then define the `Starting at`, `Ending at`, and `By` intervals.
        - **Nuance**: This type of grouping can be problematic with dynamic data, as new values outside the defined groups may not be included in existing groups, potentially creating new 'groups'. The video recommends using formulas in the source data for robust grouping with dynamic data.

#### Interactive Features with Pivot Tables:

- **Slicers (Highly Recommended)**:
    - **Purpose**: Create interactive filter buttons that are easier to use than traditional report filters.
    - **Creation**: Right-click on a field in the `PivotTable Fields` list > `Add as Slicer`.
    - **Interaction**: Click buttons to filter. Hold **`Ctrl`** to multi-select. Drag mouse to select consecutive items.
    - **Connecting Slicers to Multiple Pivots**:
        - When copying a pivot, its slicer connections are copied.
        - To connect (or disconnect) slicers from pivots: Right-click on the slicer > `Report Connections`, or select the pivot table > `Analyze` ribbon > `Filter Connections`.
- **Pivot Charts**:
    - **Creation**: Select any cell in the pivot table > `Insert` ribbon > Choose a chart type (e.g., `Column Chart`, `Line Chart`).
    - **Dynamic Update**: Pivot charts automatically update when filters are applied (e.g., via slicers) or data in the pivot table changes.
    - **Cleaning Chart Clutter**: Select the pivot chart > `PivotTable Analyze` ribbon > `Field Buttons` (turn off all). Use the `+` button on the chart itself to remove `Legend`, `Axis`, `Gridlines` etc..

### Tricks and Pro Tips Summary

The author sprinkles various useful tips throughout the video. Here’s a consolidated list:

- **Excel Shortcuts**:
    - `Ctrl + A` or `Ctrl + Shift + 8`: Select all data.
    - `Ctrl + Shift + L`: Apply or clear filters.
    - `Alt` key (briefly): Activates ribbon shortcuts (e.g., `Alt + H` then `S` then `C` for clear filters).
    - `Ctrl + Shift + Down Arrow`: Select an entire column.
    - `Alt + =`: AutoSum (automatically inserts `SUM` formula).
    - `F4` key: Changes cell reference type (relative to absolute).
- **Data Manipulation Tips**:
    - **Right-click filtering**: Right-click on any value in your data and choose `Filter` > `Filter by Selected Cell's Value` for quick filtering.
    - **Conditional Formatting for Duplicates**: Use to quickly identify data quality issues like duplicate IDs.
    - **Hiding Helper Columns/Rows**: Create intermediate calculation columns (e.g., for `LARGE` function's 'K' values) and then hide them for a cleaner report.
- **Formula Specific Tricks**:
    - **Excel 365 Spill Range Operator (`#`)**: Use after a cell reference (`B3#`) to refer to the entire spilled array, making formulas automatically expand for lists (e.g., `UNIQUE` output, dynamic criteria for `COUNTIFS`).
    - **Pre-format Spill Ranges**: Before entering a spilling formula (e.g., `FILTER`, `UNIQUE`), pre-select the expected output range and apply desired formatting (Date, Currency) so results display correctly.
    - **Dynamic Inputs**: Link formula criteria (e.g., salary threshold for `FILTER`) to a separate input cell for easy adjustments.
    - **Concatenation in `XLOOKUP`**: Use `& " " &` directly within `XLOOKUP`'s `return_array` to combine text fields (e.g., First Name and Last Name).
    - **`TEXT` function for Formatted Text**: Use `TEXT(value, "format_code")` to format numbers into text strings for custom labels (e.g., "19%").
    - **`NA()` for Chart Gaps**: Use `NA()` (instead of `0` or `""`) for values you don't want plotted in a chart series to create visual gaps or for highlighting specific items.
- **Pivot Table Best Practices and Tricks**:
    - **Name Your Tables**: Give your source data tables meaningful names (e.g., "calls") for clarity and easier reference in formulas and pivots.
    - **Clone Pivots**: Copy and paste an existing pivot table (`Ctrl + C`, `Ctrl + V`) to create a duplicate that retains most settings and slicer connections, speeding up new pivot creation.
    - **Changing Calculation Type and Formatting**: Easily adjust how values are summarised (Sum, Count, Average) and formatted (Currency, Decimals) by right-clicking on the pivot table value.
    - **Slicers for Interactivity**: Use slicers for dynamic and user-friendly filtering.
    - **Managing Slicer Connections**: After copying pivots, remember to manage which pivots are connected to which slicers via `Report Connections` or `Filter Connections`.
    - **Manual Row/Column Reordering**: Drag labels in the Rows/Columns area of the pivot table to reorder them manually, overriding default sorting (useful for logical groups like duration buckets).
    - **Consistent Conditional Formatting**: When applying conditional formatting to pivot table values, use the small pop-up option to apply the formatting to "All cells showing..." to ensure it extends across the entire relevant pivot area.

---