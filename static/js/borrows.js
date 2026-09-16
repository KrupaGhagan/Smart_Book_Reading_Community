/**
 * Vignan Library Management System - Borrows Module
 * Borrow/return management using localStorage (no backend required)
 */

const Borrows = {
    STORAGE_KEY: 'vignan_borrows',

    /**
     * Get all borrows from localStorage
     */
    async getAll() {
        try {
            return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
        } catch {
            return [];
        }
    },

    /**
     * Get borrows for a specific user
     */
    async getByUser(userId) {
        const all = await this.getAll();
        return all.filter(b => b.userId === userId);
    },

    /**
     * Get active borrows
     */
    async getActive() {
        const all = await this.getAll();
        return all.filter(b => b.status === 'active');
    },

    /**
     * Return a book - update localStorage
     */
    async returnBook(borrowId) {
        try {
            let borrows = await this.getAll();
            const index = borrows.findIndex(b => b.id === borrowId);
            if (index === -1) return { success: false, message: 'Borrow record not found!' };

            const borrow = borrows[index];
            if (borrow.status === 'returned') return { success: false, message: 'Book already returned!' };

            // Calculate fine
            const now = new Date();
            const dueDate = new Date(borrow.dueDate);
            let fine = 0;
            if (now > dueDate) {
                const overdueDays = Math.ceil((now - dueDate) / (1000 * 60 * 60 * 24));
                fine = overdueDays * 2;
            }

            // Update borrow record
            borrows[index].status = 'returned';
            borrows[index].returnDate = now.toISOString().split('T')[0];
            borrows[index].fine = fine;
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(borrows));

            // Restore book availability
            if (typeof booksDatabase !== 'undefined') {
                const book = booksDatabase.find(b => b.id === borrow.bookId);
                if (book) {
                    book.availableCopies = Math.min(book.availableCopies + 1, book.totalCopies);
                }
            }

            const message = fine > 0
                ? `Book returned. Fine of ₹${fine.toFixed(2)} applied for late return.`
                : 'Book returned successfully!';

            return { success: true, message, fine };
        } catch (error) {
            console.error('Return error:', error);
            return { success: false, message: 'Failed to return book.' };
        }
    },

    /**
     * Issue/borrow a book
     */
    async issueBook(userId, bookId) {
        try {
            const user = Utils.getCurrentUser();
            if (!user) return { success: false, message: 'Please login first.' };

            const book = (typeof booksDatabase !== 'undefined')
                ? booksDatabase.find(b => b.id === bookId)
                : null;
            if (!book) return { success: false, message: 'Book not found!' };
            if (book.availableCopies <= 0) return { success: false, message: 'Book not available!' };

            let borrows = await this.getAll();

            // Check limits
            const activeByUser = borrows.filter(b => b.userId === userId && b.status === 'active');
            if (activeByUser.length >= 3) return { success: false, message: 'Max 3 books at a time!' };
            if (activeByUser.find(b => b.bookId === bookId)) return { success: false, message: 'Already borrowed!' };

            const borrowRecord = {
                id: 'BRW_' + Date.now(),
                userId: userId,
                bookId: bookId,
                bookTitle: book.title,
                bookAuthor: book.author,
                issueDate: new Date().toISOString().split('T')[0],
                dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                returnDate: null,
                status: 'active',
                fine: 0
            };

            borrows.push(borrowRecord);
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(borrows));

            // Update book availability
            book.availableCopies--;

            return { success: true, message: `"${book.title}" borrowed successfully!`, borrow: borrowRecord };
        } catch (error) {
            console.error('Borrow error:', error);
            return { success: false, message: 'Failed to borrow book.' };
        }
    },

    /**
     * Filter borrows
     */
    async filter(status = '', query = '') {
        let borrows = await this.getAll();
        if (status) borrows = borrows.filter(b => b.status === status);
        if (query) {
            const q = query.toLowerCase();
            borrows = borrows.filter(b =>
                (b.bookTitle && b.bookTitle.toLowerCase().includes(q)) ||
                (b.bookId && b.bookId.toLowerCase().includes(q))
            );
        }
        return borrows;
    },

    /**
     * Get stats
     */
    async getStats() {
        const borrows = await this.getAll();
        const active = borrows.filter(b => b.status === 'active');
        const now = new Date();
        const overdue = active.filter(b => new Date(b.dueDate) < now);
        const fiveDays = new Date(now.getTime() + 5 * 24 * 60 * 60 * 1000);
        const dueSoon = active.filter(b => {
            const due = new Date(b.dueDate);
            return due >= now && due <= fiveDays;
        });
        const totalFine = borrows.reduce((sum, b) => sum + (b.fine || 0), 0);

        return {
            total: borrows.length,
            active: active.length,
            overdue: overdue.length,
            dueSoon: dueSoon.length,
            totalFine
        };
    }
};
